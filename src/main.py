from core import Parser

def main(link):
    Parser(link).parse()

if __name__ == '__main__':
    main('https://www.researchgate.net/search/publication?q=Process%20Mining')
    # main('https://whatmyuseragent.com/')