from core import Parser, CloudflareParser

def main(link):
    CloudflareParser(link)

if __name__ == '__main__':
    main('https://www.researchgate.net/search/publication?q=Process%20Mining')