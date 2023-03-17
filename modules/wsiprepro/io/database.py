from json import loads
from pymysql import connect

__all__ = ["LoginWSIViewer", "GetWSIInfos"]


def LoginWSIViewer():
    """Return pymysql cursor which connected to showinfos database.

    Parameters
    ----------
    None

    Returns
    -------
    cur : pymysql connect cursor
    """
    conn = connect(host="localhost", user="wsiviewer", password="1q2w3e4r", db="showinfos")
    cur = conn.cursor()

    return cur

def GetWSIInfos(cur, nameSchemaEx):
    """Organize mysql databases WSI informations to dictionary.

    Parameters
    ----------
    cur : pymysql connect cursor
        Mysql cursor pointed in mysql database.

    nameSchemaEx : string
        Viewer table name.

    Returns
    -------
    wsiinfo : Dictionary
        Organized WSI information from database table.

    Example
    -------
    >>> cur = LoginWSIViewer()
    >>> wsiluadinfo = GetWSIInfos(cur, "wsiluadinfo")
    """
    #mysql SELECT
    cur.execute("SELECT * FROM %s;"%nameSchemaEx)
    results = cur.fetchall()

    #Organized in dictionary
    wsiinfo = {}
    for data in results:
        corrdihuman = data[2]
        corrdilearn = data[3]
        pathMaskSpec = data[4]
        pathMaskAnno = data[5]
        #If not have data, It remain just None
        if bool(data[2]):
            corrdihuman = loads(corrdihuman)
        if bool(data[3]):
            corrdilearn = loads(corrdilearn)
        tmpDic = {"filepath" : data[1], "corrdihuman" : corrdihuman, "corrdilearn" : corrdilearn,
                  "maskspec" : pathMaskSpec, "maskanno" : pathMaskAnno}
        wsiinfo[data[0]] = tmpDic

    return wsiinfo
