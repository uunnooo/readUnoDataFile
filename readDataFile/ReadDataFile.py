def funcFindSaveDate(RawData) :
    """
    :param RawData :
    :return ResultData : string
    """
    import re
    import numpy as np

    if RawData[0].str.match(r'.*file.*create.*|.*start.*', flags=re.I).any() :
        listLineSample = np.array(RawData.iloc[np.where(
            RawData[0].str.match(r'.*file.*create.*|.*start.*', flags=re.I))[0][0], 0].split())
        date = listLineSample[np.where([data[0].isnumeric() for data in listLineSample])[0]]
        ResultData = date[0] + " " + date[1]
    else :
        ResultData = "0000-00-00 00:00"

    return ResultData


def funcFindSampleRate(RawData) :
    """
    :param RawData :
    :return ResultData : int
    """
    import re
    import numpy as np

    if RawData[0].str.contains(r'log.*rate|sam.*rate', flags=re.I).any() :
        listLineSample = \
            RawData.iloc[np.where(RawData[0].str.findall(r'log.*rate|sam.*rate', flags=re.I))[0][0], 0].split()
        ResultData = float(listLineSample[np.where([data[0].isnumeric() for data in listLineSample])[0][0]])
    else :
        ResultData = 200.0

    return ResultData


def funcFindHeader(RawData) :

    """
    Find name of data columns and number of start line for rawdata

    :param RawData : [list] str type list of rawdata each line
    :return: number of line column and data
    """

    import numpy as np

    regWordDelimiter = [r' ', r'\t', r',']
    regCharacter = {'letter' : r'[a-zA-Z]', 'number' : r'[0-9.]', 'special' : r'[^\sa-zA-Z0-9+-.]'}

    # 문장수로 구분
    indexDelimiter = np.argmax([np.sum(list(map(len, list(RawData[0].str.findall(delimiter)))))
                                for delimiter in regWordDelimiter])
    delimiter = regWordDelimiter[indexDelimiter]
    tmpContinues1 = list(map(len, list(RawData[0].str.findall(delimiter))))
    tmpContinues2 = [[i, k] for i, k in enumerate(tmpContinues1) if abs((tmpContinues1[i] - tmpContinues1[i - 1])) != 0]
    continuesWord = list(zip(*tmpContinues2))

    # 문자수로 구분
    tmpContinues1 = [list(map(len, list(RawData[0].str.findall(reg)))) for reg in regCharacter.values()]
    tmpContinues2 = [[[i, k] for i, k in enumerate(data) if abs((data[i] - data[i - 1])) > 2] for data in tmpContinues1]
    continuesChar = [list(zip(*data)) for data in tmpContinues2]

    lineNumLastWordChangeLine = continuesWord[0][-1]
    lineNumLastCharChangeLine = [data[0][-1] for data in continuesChar]

    '''
    각각의 문자들의 형식을 인식하고 문자들의 글자수를 인식한다.
    1. 데이터시작 위치 찾기      
     (1) 구분자에 의해 구분된 단락들의 변화가 없는 위치
     (2) 숫자가 가장 많고, 글자수의 변화가 없는 위치
     (3) 부호 및 소수점을 제외한 특수문자가 없으면서 글자수의 변화가 없는 위치
      - 숫자의 자리수가 변하면서 데이터들이 변하는 경우 있음
     (4) 구분자로 이용 줄을 나눴을때, (1)~(3)와 같은 경우 채택으로 변경
     → 파일에서 사용하는 구분자는 카운트가 가장 많은 특수문자로 구분(문장에서의 구분자와는 다르다)
     (5) 구분자 이용 단어들의 갯수와 (1)~(3) 중에 같은 경우가 없을때는 어떻해 해야 되는지에 대해서 고민해봐야댐
      
    2. 채널이름 위치 찾기
     (1) 영문자가 가장 많은 위치
     (2) 데이터 시작위치와의 거리 차이
      weightedLetter = L X D
       L : 라인에 있는 영문자수
       D : 데이터와의 시작위치(멀어질수록 라인 당 0.1의 Weight 차감 ,10라인 밖에 있는 라인들은 후보군 제외)
    '''
    lineNumStartData = lineNumLastCharChangeLine[np.argmin([abs(line - lineNumLastWordChangeLine)
                                                            for line in lineNumLastCharChangeLine])]
    dist = [1 - 0.1*(lineNumStartData - line) for line in continuesChar[0][0] if lineNumStartData - line > 0]
    lineNumColumn = continuesChar[0][0][np.argmax([continuesChar[0][1][i] * k for i, k in enumerate(dist)])]

    return lineNumColumn, lineNumStartData


def funcMakeDataFrame(RawData, *lineNum : int) :
    """
    :param RawData:
    :param lineNum:
    :return:
    """

    import pandas as pd
    from _ListDelimiter_ import funcFindDelimiter

    # 라인에 대한 넘버 정보 하나일때, 즉 데이터 정의나 단위 정보일때
    if len(lineNum) < 2 :
        listLineNum = [lineNum[0], lineNum[0] + 1]
        # 형을 맞춰주기 위함
        lineData = RawData.iloc[listLineNum[0]: listLineNum[1], 0].str.rstrip()
        separator = funcFindDelimiter(lineData)

        # 채널 및 단위를 한개 이상의 Seperator를 사용할때를 위한 조건
        if len(separator) > 1:
            regx = [f"{separator[0]}", f"{separator[1]}"]
            tmpData1 = lineData.str.split(regx[1], expand=True)
            tmpData2 = tmpData1[tmpData1.astype(bool)].dropna(axis=1).copy()
            tmpData3 = tmpData2.iloc[0].str.strip()
            ResultData = tmpData3.str.split(regx[0], expand=True)

        else:
            regx = [f"{separator[0]}"]
            tmpListUnit = RawData.iloc[listLineNum[0] + 1: listLineNum[1] + 1, 0]\
                .str.split(regx[0], expand=True).copy().T
            listUnit = tmpListUnit.iloc[:, 0].str.strip()
            tmpResultData = lineData.str.split(regx[0], expand=True).copy().T
            listName = tmpResultData.iloc[:, 0].str.strip()

            if listName.shape[0] is not listUnit.shape[0] :
                listUnit = pd.Series(["-" for i in range(0, listName.shape[0])])

            ResultData = pd.concat([listName, listUnit], axis=1)

    # 라인에 대한 넘버 정보가 두개 이상일때, 즉 데이터에 대한 행렬일때
    else :
        listLineNum = [lineNum[0], lineNum[1]]
        # 형을 맞춰주기 위함
        lineData = RawData.iloc[listLineNum[0]: listLineNum[1], 0]
        separator = funcFindDelimiter(lineData)
        regx = [f"{separator[0]}"]
        listName = lineData.str.rstrip().str.split(regx[0], expand=True).copy()
        # Remove characters in the end of line
        ResultData = listName.astype("double")

    return ResultData


def funcReadDataFile(FileName) :

    import pandas as pd
    import numpy as np

    rawData = pd.read_csv(FileName, engine='c', encoding='cp1252', on_bad_lines='skip', header=None,
                          skip_blank_lines=True, keep_default_na=False)
    lineNumColumns, lineNumData = funcFindHeader(rawData)
    saveDate = funcFindSaveDate(rawData.iloc[0:lineNumColumns, :])
    sampleRate = funcFindSampleRate(rawData.iloc[0:lineNumColumns, :])
    dataName = funcMakeDataFrame(rawData, lineNumColumns)
    tmpData = funcMakeDataFrame(rawData, lineNumData, -1)
    rawDF = tmpData.copy()
    rawDF.columns = dataName.transpose().values.tolist()
    rawDF.columns.names = ["Name", "Unit"]
    rawDF.reset_index(inplace=True, drop=True)

    indStr = np.where(np.array(list(FileName)) == "/")[0]
    savePath = FileName[:indStr[-1]+1]
    tmpName = FileName[indStr[-1]+1:-4]

    if pd.Series(pd.Series(saveDate).str.findall(r'\d{4}-\d{2}-\d{2}')[0]).any() and \
            pd.Series(pd.Series(saveDate).str.findall(r'\d{2}:\d{2}')[0]).any() :

        tmpDate = pd.Series(pd.Series(saveDate).str.findall(r'\d{4}-\d{2}-\d{2}')[0]).str.split("-")[0]
        tmpTime = pd.Series(pd.Series(saveDate).str.findall(r'\d{2}:\d{2}')[0]).str.split(":")[0]
        saveNameDate = tmpDate[0][2:4] + tmpDate[1] + tmpDate[2] + tmpTime[0] + tmpTime[1]
    else :
        saveNameDate = "0000000000"

    saveName = savePath+tmpName+"-"+saveNameDate+".csv"
    rawDF.to_csv(saveName, index=False)
    return tmpName, rawDF

def ReadDataFile(*FileName) :

    from PyQt5 import Qt

    dfList = []
    if not FileName :
        app = Qt.QApplication([])
        fName = Qt.QFileDialog.getOpenFileNames(None,  'Select File', "", 'Datafile(*.txt);;Datafile(*.vbo)')
        [dfList.append(funcReadDataFile(file)) for file in fName[0]]
    else :
        [dfList.append(funcReadDataFile(file)) for file in FileName]

    return dfList

if __name__ == "__main__" :
    dfList = ReadDataFile()
    print(dfList)
