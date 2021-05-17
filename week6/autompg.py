from collections import namedtuple
import csv

Record = namedtuple('Record', ['mpg', 'year', 'make', 'model'])

class AutoMPGData():
    def __init__(self):
        self.data = []
        ## call _load_data() to populate the data attribute
        self._load_data()
        
    def __iter__(self):
        """Return iterable class."""
        return iter(self.data)

    def _load_data(self):
        """Load a data file into AutoMPG objects and add them to state."""
        try:
            with open('auto-mpg.clean.txt', 'r') as clean_data:
                ## generator to populate self.data with AutoMPG objects
                for auto_record in csv.reader(clean_data, delimiter= ' ', skipinitialspace= True):
                    print(auto_record)
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
                    
                    ## append the auto object
                    self.data.append(AutoMPG(auto.make, auto.model, auto.year, auto.mpg))
        except:
            ## file not present, clean it and the load it
            self._clean_data()
            self._load_data()
        
    def _clean_data(self):
        """Read the auto-mpg dataset and generates a 'cleansed', whitespace-delimited file."""
        try:
            with open('auto-mpg.data.txt', 'r') as dirty_data:
                with open('auto-mpg.clean.txt', 'w') as clean_data:
                    for row in csv.reader(dirty_data):
                        clean_data.write(row[0].expandtabs(1) + '\n')
        except FileNotFoundError:
            print(f'Could not open file!')

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
    
    # def __repr__(self):
    #     """Return canonical representation of the class."""
    #     return f'AutoMPG({self.make}, {self.model}, {self.year}, {self.mpg})'
        
    # def __str__(self):
    #     """Return string representation of the class."""
    #     return

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
    ## iterate through AutoMPGData()
    for auto in AutoMPGData():
        # print(auto)
        pass

if __name__ == '__main__':
    main()