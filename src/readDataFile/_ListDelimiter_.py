listDelimiter = [[' '],
                 ['\t'],
                 ['[', ']'],
                 ['(', ')'],
                 ['{', '}'],
                 ["'", "'"],
                 ['<', '>'],
                 ]

def funcFindDelimiter(line):
    import pandas as pd
    import numpy as np
    from collections import Counter

    listSelASC = []

    listSPCharacter = line.str.findall(r'\W')
    CNTASC = Counter(listSPCharacter.iloc[0])
    listASC = list(CNTASC.keys())
    listCNT = list(CNTASC.values())
    # [listSelASC.append(listASC[np.argmax(listCNT)]) for i in range(0, 3)]
    if len(listASC) > 2 :
        for i in range(0, 3):
            listSelASC.append(listASC[np.argmax(listCNT)])
            listASC.pop(np.argmax(listCNT))
            listCNT.pop(np.argmax(listCNT))
    else :
        for i in range(0, len(listASC)):
            listSelASC.append(listASC[np.argmax(listCNT)])
            listASC.pop(np.argmax(listCNT))
            listCNT.pop(np.argmax(listCNT))
    '''
    구분자를 찾기 위한 구문 필요
    일반적으로 공백에 대한 카운트가 가장 많다.
    그럼 실제 공백일때와 공백이 아닐때의 비교는 어떻해?
    1. 가장 많은 특수 문자를 추린다.
    2. 가장 많은 특수 문자를 3가지를 선정한다
    3. 가장 많이 사용된 특수문자 조합을 비교한다.(쌍으로 비교)
    4. 쌍으로 비교했을때 많이 사용된 3가지 중 2가지에 포함된다면 그 문자를 구분자로 인식한다.
    5. 그게 아니라면 공백 이나 탭으로 인식하고 그에 따라 처리한다.
    '''
    tmpFlagCNT1 = []

    tmpSeriesLine = pd.Series(listSelASC)
    [tmpFlagCNT1.append(np.where(tmpSeriesLine.isin(pattern))[0].size)
     for pattern in listDelimiter] # 정해진 패턴과 일치하는 패턴수 파악
    flagDelimiter = np.argmax(tmpFlagCNT1) # 가장 많이 일치하는 패턴 선정(index)

    if flagDelimiter > 0 :
        delimiter = listDelimiter[flagDelimiter]
    elif flagDelimiter == 0: # 공백이나 Tab일때로 판단
        if tmpFlagCNT1[1] == 1 :
            delimiter = listDelimiter[1]
        else :
            delimiter = listDelimiter[0]
    return delimiter
