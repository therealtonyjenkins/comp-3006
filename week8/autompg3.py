import argparse
from collections import defaultdict, namedtuple
import csv
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from os import path
import requests
import sys

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
        self.response_code = None
        ## call _load_data() to populate the data attribute
        self._load_data()
        
    def __iter__(self):
        """Return iterable class."""
        return iter(self.data)
    
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

        def __correct_car_make(car_make):
            """ Corrects given make names to a standard make name. """
            ## define model corrections
            correct_makes = {
                '\'chevroelt\'': '\'chevrolet\'',
                '\'chevy\'': '\'chevrolet\'',
                '\'maxda\'': '\'mazda\'',
                '\'mercedes\'-\'benz\'': 'mercedes',
                '\'toyouta\'': '\'toyota\'',
                '\'vokswagen\'': '\'volkswagen\'',
                '\'vw\'': '\'volkswagen\''
            }
            ## return corrected make
            return correct_makes[car_make] if car_make in correct_makes.keys() else car_make

        logger.debug('checking auto-mpg.data.txt')
        if not path.exists('auto-mpg.data.txt'):
            ## file not present, get it
            logger.debug('getting auto-mpg.data.txt')
            self._get_data()
        if not path.exists('auto-mpg.clean.txt'):
            ## file not present, clean it
            self._clean_data()
        
        ## we got the data and we cleaned it
        logger.debug('checking auto-mpg.clean.txt')
        try:
            with open('auto-mpg.clean.txt', 'r') as clean_data:
                logger.debug('auto-mpg.clean.txt exists')
                ## counter for auto objects
                counter = 0
                logger.debug('Parsing auto-mpg.clean.txt into AutoMPG objects')
                for auto_record in csv.reader(clean_data, delimiter= ' ', skipinitialspace= True):
                    ## split the car name into 2 tokens
                    split = auto_record[8].split(' ', 1)
                    ## handle the case for 'subaru'
                    if len(split) < 2:
                        make = f'\'{split[0]}\''
                        auto = Record(auto_record[0], auto_record[6], __correct_car_make(make), '')
                    elif len(split) == 2:
                        make = f'\'{split[0]}\''
                        ## handle the case for '\' cuda'
                        clean_model = split[1].replace('\'', '')
                        model = f'\'{clean_model}\''
                        auto = Record(auto_record[0], auto_record[6], __correct_car_make(make), model)
                    counter += 1
                    ## append the auto object
                    self.data.append(AutoMPG(auto.make, auto.model, auto.year, auto.mpg))
        except Exception as e:
            logger.info(f'Error occurred: {e}')
        
    def _clean_data(self):
        """Read the auto-mpg dataset and generates a 'cleansed', whitespace-delimited file."""
        if not path.exists('auto-mpg.data.txt'):
            logger.info('Could not find auto-mpg.data.txt in the current working directory')
            sys.exit()
        else:
            try:
                with open('auto-mpg.data.txt', 'r') as dirty_data:
                    with open('auto-mpg.clean.txt', 'w') as clean_data:
                        ## counter for row writes
                        counter = 0
                        for row in csv.reader(dirty_data):
                            clean_data.write(row[0].expandtabs(1) + '\n')
                            counter +=1
            except Exception as e:
                logger.info('File error occurred: {e}. Exiting')
                sys.exit()

    def mpg_by_year(self):
        """Returns a dictionary where the keys are the years that are present in the dataset and the values are the 
        average MPG for all cars in the year. """
        ## create reference dict and aggregated dict
        reference_mpgs = defaultdict(list)
        year_avg_mpgs = defaultdict(int)
        ## loop through the data and add to both dicts
        for auto in self.data:
            ## get the year
            the_year = auto.year
            ## maintain a list of mpgs for each key=year
            reference_mpgs[the_year].append(auto.mpg)
            ## update the cumulative mpg as we read auto objects
            year_avg_mpgs[the_year] = sum(reference_mpgs[the_year]) / len(reference_mpgs[the_year])
        return year_avg_mpgs

    def mpg_by_make(self):
        """Returns a dictionary where the keys are the makes that are present in the dataset and the values are the
        average MPG for all cars of that make."""
        ## create reference dict and aggregated dict
        reference_mpgs = defaultdict(list)
        make_avg_mpgs = defaultdict(str)
        ## loop through the data and add to both dicts
        for auto in self.data:
            ## get the year
            the_make = auto.make
            ## maintain a list of mpgs for each key=make
            reference_mpgs[the_make].append(auto.mpg)
            ## update the cumulative mpg as we read auto objects
            make_avg_mpgs[the_make] = sum(reference_mpgs[the_make]) / len(reference_mpgs[the_make])
        return make_avg_mpgs

    def sort_by_default(self):
        """Sorts the data attribute by make, model, year, then mpg."""
        self.data.sort()

    def sort_by_year(self):
        """Sorts the data attribute by year first."""
        logger.debug('Sorting AutoMPG objects by year')
        self.data.sort(key= lambda x: (x.year, x.make, x.model, x.mpg))

    def sort_by_mpg(self):
        """Sorts the data attribute by mpg first."""
        logger.debug('Sorting AutoMPG objects by mpg')
        self.data.sort(key= lambda x: (x.mpg, x.make, x.model, x.year))

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
    parser.add_argument('mpg_by_year', metavar= 'mpg_by_year', help= 'Output data to summary of mpg by year.', type= str)
    parser.add_argument('mpg_by_make', metavar= 'mpg_by_year', help= 'Output data to summary of mpg by year.', type= str)
    parser.add_argument('-s', '--sort', metavar= '<sort order>', choices = ['year', 'mpg', 'default'], type= str, dest= 'sort_order', default= 'default')
    parser.add_argument('-o', '--ofile', metavar= '<outfile>', dest= 'output_file', type= str, default= 'std_out')
    parser.add_argument('-p', '--plot', metavar= '<plot>', dest= 'plot_file', type= str, default= 'none')
    args = parser.parse_args()

    if args.command == 'print':
        ## instantiate AutoMPGData
        autos = AutoMPGData()

        ## do sorting
        if args.sort_order == 'year':
            autos.sort_by_year()
        elif args.sort_order == 'mpg':
             autos.sort_by_mpg()
        else:
            autos.sort_by_default()

        ## check which aggregation we should do
        if args.mpg_by_year:
            ## get the dictionary
            agg = AutoMPGData.mpg_by_year()
            csv_colunms = ['year', 'avg_mpg']

            if args.plot != 'none':
                if args.output_file != 'std_out':
                    ## output mpg_by_year RAW DATA to csv
                    try:
                        with open(args.output_file, 'w') as outfile:
                            auto_writer = csv.DictWriter(outfile, fieldnames= csv_colunms)
                            for key in agg.keys():
                                auto_writer.writerow(key, agg[key])
                    except Exception as e:
                        print('Something bad happened')
                else:
                    ## output mpg_by_year RAW DATA to stdout
                    for key in agg.keys():
                        print(f'\'{key}\', \'{agg[key]}\'', file= sys.stdout)
            else:
                if args.output_file != 'std_out':
                    ## output mpg_by_year PLOT to file
                    pass
                else:
                    ## output mpg_by_year PLOT to stdout
                    pass
        elif args.mpg_by_make:
            if args.plot != 'none':
                if args.output_file != 'std_out':
                    pass
                else:
                    pass
            else:
                if args.output_file != 'std_out':
                    pass
                else:
                    pass

        ## do output
        if args.output_file != 'std_out':
            ## write auto data to file
            try:
                with open(args.output_file, 'w') as outfile:
                    auto_writer = csv.writer(outfile, delimiter= ',', quotechar= '"', quoting= csv.QUOTE_NONE)
                    for auto in autos:
                        line = [auto.make, auto.model, auto.year, auto.mpg]
                        auto_writer.writerow(line)
            except Exception as e:
                print('Something bad happened')
        else:
            ## write auto data to standard output
            for auto in autos:
                print(auto, file= sys.stdout)

if __name__ == '__main__':
    main()