from parsers import IEEEParser

def main(link):
    IEEEParser(link).parse()

if __name__ == '__main__':
    main('https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Process%20Mining&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&ranges=2025_2025_Year')
    # main('https://whatmyuseragent.com/')