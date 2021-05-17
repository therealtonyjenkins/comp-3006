from collections import namedtuple
import logging
import requests
import csv
import sys
import argparse
from os import path

## handle logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

## file handler
fh = logging.FileHandler('autompg2.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

## stream handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger.addHandler(sh)

## Record setup
Record = namedtuple('Record', ['mpg', 'year', 'make', 'model'])

class AutoMPGData():
    def __init__(self):
        self.data = []
        ## call _load_data() to populate the data attribute
        self._load_data()
        self.response_code = None
        
    def __iter__(self):
        """Return iterable class."""
        return iter(self.data)
    
    def sort_by_default(self):
        """Sorts the data attribute by make, model, year, then mpg."""
        # self.data.sort(key= lambda x: (x.make, x.model, x.year, x.mpg))
        self.data.sort()

    def sort_by_year(self):
        """Sorts the data attribute by year first."""
        logger.debug('Sorting AutoMPG objects by year')
        self.data.sort(key= lambda x: (x.year, x.make, x.model, x.mpg))

    def sort_by_mpg(self):
        """Sorts the data attribute by mpg first."""
        logger.debug('Sorting AutoMPG objects by mpg')
        self.data.sort(key= lambda x: (x.mpg, x.make, x.model, x.year))

    def _get_data(self):
        """Downloads data from the interwebs to be loaded into the data attribute."""
        try:
            
            with open('auto-mpg.data.txt', 'w') as data_file:
                url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data'
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    logger.debug(f'response code from url: 200')
                    self.response_code = 200
                    for line in r.iter_lines():
                        data_file.write(line.decode() + '\n')
                else:
                    self.response_code = r.status_code
                    logger.info(f'{url} returned status code {r.status_code}')
        except Exception as e:
            logger.info(f'Unexpected error writing to file {str(e)}. Exiting.')
            sys.exit()

    def _load_data(self):
        """Load a data file into AutoMPG objects and add them to state."""
        logger.debug('checking auto-mpg.data.txt')
        if not path.exists('auto-mpg.data.txt'):
            ## file not present, get it
            logger.debug('getting auto-mpg.data.txt')
            self._get_data()
        if not path.exists('auto-mpg.clean.txt'):
            ## file not present, clean it
            self._clean_data()
        logger.debug('checking auto-mpg.clean.txt')
        try:
            with open('auto-mpg.clean.txt', 'r') as clean_data:
                logger.debug('auto-mpg.clean.txt exists')
                ## generator to populate self.data with AutoMPG objects
                ## counter for auto objects
                counter = 0
                logger.debug('Parsing auto-mpg.clean.txt into AutoMPG objects')
                for auto_record in csv.reader(clean_data, delimiter= ' ', skipinitialspace= True):
                    ## split the car name into 2 tokens
                    split = auto_record[8].split(' ', 1)

                    ## handle the case for 'subaru'
                    if len(split) < 2:
                        make = f'\'{split[0]}\''
                        auto = Record(auto_record[0], auto_record[6], make, '')
                    elif len(split) == 2:
                        make = f'\'{split[0]}\''
                        ## handle the case for '\' cuda'
                        clean_model = split[1].replace('\'', '')
                        model = f'\'{clean_model}\''
                        auto = Record(auto_record[0], auto_record[6], make, model)
                    counter += 1
                    ## append the auto object
                    self.data.append(AutoMPG(auto.make, auto.model, auto.year, auto.mpg))
        except Exception as e:
            logger.info(f'File read error occurred: {e}')
        
    def _clean_data(self):
        """Read the auto-mpg dataset and generates a 'cleansed', whitespace-delimited file."""
        # logger.debug('checking auto-mpg.data.txt')
        if not path.exists('auto-mpg.data.txt'):
            logger.info('Could not find auto-mpg.data.txt in the current working directory')
            sys.exit()
        else:
            try:
                with open('auto-mpg.data.txt', 'r') as dirty_data:
                    with open('auto-mpg.clean.txt', 'w') as clean_data:
                        # logger.debug('auto-mpg.data.txt exists')
                        ## counter for row writes
                        counter = 0
                        for row in csv.reader(dirty_data):
                            clean_data.write(row[0].expandtabs(1) + '\n')
                            counter +=1
            except Exception as e:
                logger.info('File error occurred: {e}. Exiting')
                sys.exit()

class AutoMPG():
    def __init__(self, make, model, year, mpg):
        ## handle cases for year
        if len(str(year)) == 1:
            self.year = int('190' + str(year))
        elif len(str(year)) == 2:
            self.year = int('19' + str(year))

        self.make = str(make)
        self.model = str(model)
        self.mpg = float(mpg)
    
    def __repr__(self):
        """Return canonical representation of the class."""
        return f'AutoMPG({self.make}, {self.model}, {self.year}, {self.mpg})'
        
    def __str__(self):
        """Return string representation of the class."""
        return self.__repr__()

    def __eq__(self, other):
        """Return a boolean if the AutomMPG object and a comparison object are equal."""
        if type(self) == type(other):
            return (self.make, self.model, self.year, self.mpg) == (other.make, other.model, other.year, other.mpg)
        else:
            return NotImplemented

    def __lt__(self, other):
        """Return a boolean if the AutomMPG object is less than a comparison object."""
        if type(self) == type(other):
            ## if 'make' are the same, then defer to 'model'
            if self.make == other.make:
                return (self.model, self.year, self.mpg) < (other.model, other.year, other.mpg)
            else:
                return (self.make, self.model, self.year, self.mpg) < (other.make, other.model, other.year, other.mpg)
        else:
            raise NotImplemented

    def __hash__(self):
        """Returns hash for the objects."""
        obj = (self.make, self.model, self.year, self.mpg)
        return hash(obj)

def main():
    ## handle argparse setup
    parser = argparse.ArgumentParser(description= 'Analyze Auto MPG data set', epilog= 'Vroom vroom!')
    parser.add_argument('command', metavar= '<command>', help= 'The command to execute.', type= str)
    parser.add_argument('-s', '--sort', metavar= '<sort order>', choices = ['year', 'mpg', 'default'], type= str, dest= 'sort_order', default= 'default')
    args = parser.parse_args()

    if args.command != 'print':
        ## exit program for invalid commands
        print(f'{args.command} is not a valid command! Exiting')
        sys.exit()
    else:
        ## instantiate AutoMPGData
        autos = AutoMPGData()

        ## check how to sort
        if args.sort_order == 'year':
            autos.sort_by_year()
        elif args.sort_order == 'mpg':
             autos.sort_by_mpg()
        else:
            autos.sort_by_default()

    ## iterate through AutoMPGData()
    for auto in autos:
        logger.info(str(auto))

if __name__ == '__main__':
    main()