from collections import namedtuple
import csv
from datetime import timezone, datetime
import logging
import re

## some globals
dataset = 'Ethereum_Historical_Data.csv'

## handle logger setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

## file handler
fh = logging.FileHandler('data_reader.log', 'w')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

## stream handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger.addHandler(sh)

## named tuples for easier attribute-accessing
ETHRecord = namedtuple('ETHRecord', ['date', 'price', 'open', 'high', 'low', 'volume', 'perc_change'])

class ETHPriceReader():
    def __init__(self):
        pass

    def _data_streamer(self):
        pass

    def _cleanse_data(self, header):
        """ Generic data-reading and cleansing method to be used on a dataset. 
        
        Arguments
        ---------
        header: bool; required
        A boolean indicating whether the data contains a header row.
        """

        ## helper methods
        def _convert_to_volume(vol):
            """ Converts an abbreviated number to a float. 
            
            Arguments
            ---------
            vol: str; required
            A string-representation of a volume, denoted with a K or M for thousands and millions.
            """
            if vol.find('M') != -1:
                ## split on 'K' convert to float and multiply by 1000000
                return float(vol.split('M')[0].strip()) * 1000000
            elif vol.find('K') != -1:
                ## split on 'K' convert to float and multiply by 1000
                return float(vol.split('K')[0].strip()) * 1000
            elif vol.find('-') != -1:
                ## null value found, return 0
                return 0.00
            else:
                raise Exception(f'Found an unhandled character in volume: [{vol}]')

        def _convert_to_true_percentage(perc):
            """ Converts a formatted percentage to a float. 
            
            Arguments
            ---------
            perc: str; required
            A string-representation of a percentage, denoted with %.
            """
            return float(perc.split('%')[0].strip()) / 100

        def _convert_to_true_float(num):
            """ Removes any extraneous characters from a formatted numeric. 
            
            Arguments
            ---------
            num: str; required
            A string-representation of a volume, denoted with a K or M for thousands and millions.
            """
            return float(num.replace(',', ''))

        ## read in dataset
        try:
            with open(dataset, 'r') as data:
                datareader = csv.reader(data, delimiter= ',', quotechar= '"')
                with open(dataset + '.clean.csv', 'w') as clean_data:
                    for index, line in enumerate(datareader):
                        ## skip line cleansing if header is present but write to output
                        if header and index == 0:
                            clean_data.write(line[0])
                            logger.error(f'[{datetime.now(tz= timezone.utc)}] INFO Header row present; skipping')
                            continue
                        else:
                            ## cleanse line
                            clean_data.writelines(
                                datetime.strftime(line[0]),
                                _convert_to_true_float(line[1]),
                                _convert_to_true_float(line[2]),
                                _convert_to_true_float(line[3]),
                                _convert_to_true_float(line[4]),
                                _convert_to_volume(line[5]),
                                _convert_to_true_percentage(line[6])
                            )

        except FileNotFoundError as e:
            logger.error(f'[{datetime.now(tz= timezone.utc)}] ERROR Could not find dataset \"{dataset}\"')

class ETHPriceSnapshot():
    def __init__(self):
        pass

def main():
    ETHPriceReader()._cleanse_data(header= True)

if __name__ == '__main__':
    main()