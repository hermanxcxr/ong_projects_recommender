from extraction import Extraction
from transform import Transform
from db_search import DbSearch

if __name__ == '__main__':
    task = input('Buscar coincidencias de proyectos (y/n): ')

    if task == 'y':

        country = input('Country: ')
        funding = input('Funding: ')
        keywords = input('Keywords: ')

        db_search = DbSearch(country,funding,keywords)
        db_search.db_searcher()

        
    elif task == '0':

        extraction = Extraction(
            '../../../selenium_driver/chromedriver96.exe',
            'https://www.grants.gov/web/grants/search-grants.html',
            'https://www.grants.gov/view-opportunity.html?oppId='
            )
        extraction.extractor()

        transform = Transform()
        transform.db_transformer()