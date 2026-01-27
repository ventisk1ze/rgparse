import traceback
from parsers import IEEEParser

def main(link):
    try:
        p = IEEEParser(link)
        p.parse()
    except Exception as e:
        traceback.print_exception(e)
        p.save_to_html()


if __name__ == '__main__':
    main('https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=Process%20Mining&highlight=true&returnType=SEARCH&matchPubs=true&refinementName=Publication%20Topics&pageNumber=1&refinements=PublicationTopics:Process%20Mining&ranges=2025_2025_Year&returnFacets=ALL')