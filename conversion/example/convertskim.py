import pandas as pd

path = './'

def save_to_csv(skimfile,zonefile):
    zones = pd.read_csv(path + zonefile,header=None)
    zonelist = zones[0].tolist()
    skim = pd.read_csv(path + skimfile,header=None)
    skim.columns = zonelist
    skim.index = zonelist
    skim.to_csv(path + "Headers" +  skimfile )


# change the file name to skim csv file, zone csv file
save_to_csv('skimmatrix.csv','zone.csv')