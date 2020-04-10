import glob
import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from shutil import copyfile
from tqdm import tqdm

#github = "https://raw.githubusercontent.com/SimonJMurphy/TESSSB9/master"
github = "."

# Read the SB9 data tables
maindata = pd.read_csv(f"{github}/data/SB9public/Main.dta", names=["SysNum","J1900","J2000","component","mag1","filter1","mag2","filter2","spt1","spt2"], delimiter='|')

names = ["SysNum", "OrbNum", "Porb", "Porb_err", "tp", "tp_err", "tp_flag", "ecc", "ecc_err", "omega", "omega_err", "K1", "K1_err", "K2", "K2_er", "gamma", "gamma_err", "rmsRV1", "rmsRV2", "numRV1", "numRV2", "Grade", "Bibcode", "Contributor", "Accessibility", "JDRef"]
orbits = pd.read_csv(f"{github}/data/SB9public/Orbits.dta",names=names, delimiter="|")

# Read Kareem's SB9+TESS cross-match
df = pd.read_csv(f"{github}/data/sb9_x_gaia_with_tess_all_sectors.csv")

# find orbits with fewest null values. 
### Should probably replace with the orbit with most measured RVs. ###
xorbs = orbits.loc[orbits.notnull().sum(1).groupby(orbits.SysNum).idxmax()]

# merge our TIC-matched df with the good orbits (kind of weird, but we don't want duplicates)
xdf = df.merge(xorbs,left_on="SB9_id",right_on='SysNum')


# Loop over files and find unique TICS. This requires connection to silo2 server
print("Gathering information on TESS lightcurves from the SILO server...")
files = []
for sector in list(range(1, 22)):
    files.extend(
        glob.glob("/Volumes/silo2/dhey3294/TESS/sector_" + str(sector) + "/tess*.fits")
    )

tics = [a.split("_")[1].split("/")[-1].split("-")[2].lstrip("0") for a in files]

# rescue with the online files if silo2 is out of action
if len(tics) < 1:
    print("There may be an issue with the SILO server. Rescuing using local files...")
    files.extend(
            glob.glob(f"{github}/data/TESS_plots/LKs/*png")
        )
    tics = [a.split("/")[-1].split(".")[0] for a in files]

unique_tics = np.unique(tics)


print("Cross-matching and producing dataframe...")

# keep only the systems we have a TESS LK of.
tf = xdf[xdf["TIC"].isin(unique_tics)]

# We mostly want to use log p, and we also want abs mag and the number of RVs
tf["logp"] = np.log10(tf["P"])
tf['absmag'] = tf['phot_g_mean_mag'].values - 5 * np.log10(1/(tf['parallax'].values)*1000) + 5
numRVs = []
for rv1,rv2 in zip(tf['numRV1'].values,tf['numRV2'].values):
    if np.isnan(rv1) and np.isnan(rv2):
        numRVs.append(-1)
    else:
        numRVs.append(np.nanmax([rv1,rv2]))
tf["numRVs"] = numRVs

# construct filename dataframe
fts = [f"{github}/data/TESS_plots/FTs/{ticid}.png" for ticid in tf["TIC"].values]
lks = [f"{github}/data/TESS_plots/LKs/{ticid}.png" for ticid in tf["TIC"].values]
scaled_fts = [f"{github}/data/TESS_plots/scaled_FTs/{ticid}.png" for ticid in tf["TIC"].values]
folded_lks = [f"{github}/data/TESS_plots/folded_LKs/{ticid}.png" for ticid in tf["TIC"].values]
tic_pg = pd.DataFrame({
    'ID': tf["TIC"].values,
    'fts': fts,
    'lks': lks,
    'scaled_fts': scaled_fts,
    'folded_lks': folded_lks
})

# overwrite the dataframe to include these filenames
tf = tf.merge(tic_pg,left_on="TIC",right_on='ID')

# write this df to csv
tf.to_csv("plot_df.csv",index=False)

## Various plotting functions

# read a lightcurve into memory
def get_lightcurve(unique_tic):
    unique_tic = str(unique_tic)
    indices = [i for i, x in enumerate(tics) if x == unique_tic]
    lc = lk.TessLightCurveFile(files[indices[0]]).PDCSAP_FLUX.normalize()
    for index in indices[1:]:
        lc = lc.append(lk.TessLightCurveFile(files[index]).PDCSAP_FLUX.normalize())
    lc = lc.remove_nans()
    return lc

def save_fits_files_locally(files):
    print("saving fits files locally...")
    destination = "data/TESS_fits/"
    
    for f in tqdm(files):
        this_tic = f.split("_")[1].split("/")[-1].split("-")[2].lstrip("0")
        if this_tic in tf["TIC"].values:
            fits = f.split("/")[-2]+"/"+f.split("/")[-1]
            os.makedirs(os.path.dirname(destination+fits), exist_ok=True)
            copyfile(f,destination+fits)

def save_lc(ticnum,lc):
    print(f"saving lightcurve at data/TESS_ascii/{ticnum}_lightcurve.csv")
    magnitude = -2.5 * np.log10(lc.flux)
    magnitude = magnitude - np.average(magnitude)
    np.savetxt(f"data/TESS_lcs/{ticnum}_lightcurve.csv",np.array([lc.time,magnitude]).T, delimiter=" ")

def produce_lks(ticnum,lc):
    print(f"making data/TESS_plots/LKs/{ticnum}.png")
    fig = lc.plot()
    plt.savefig(f"data/TESS_plots/LKs/{ticnum}.png",bbox_inches='tight')
    plt.clf()
    plt.close('all')

def produce_folded_lks(ticnum,lc):
    print(f"making data/TESS_plots/folded_LKs/{ticnum}.png")
    p = tf.query(f"TIC=={ticnum}")["P"].values[0]
    fig = lc.fold(period=p).plot()
    plt.savefig(f"data/TESS_plots/folded_LKs/{ticnum}.png",bbox_inches='tight')
    plt.clf()
    plt.close('all')

def produce_fts(ticnum,lc):
    print(f"making data/TESS_plots/FTs/{ticnum}.png")
    p = tf.query(f"TIC=={ticnum}")["P"].values[0]
    fmax = 15
    fig = lc.to_periodogram(maximum_frequency=fmax).plot()
    if 1/p < fmax:
        plt.axvline(1.0/p,color='r', ls='--', lw=0.8)
    plt.xlim(0,fmax)
    plt.ylim(bottom=0)
    plt.savefig(f"data/TESS_plots/FTs/{ticnum}.png",bbox_inches='tight')
    plt.clf()
    plt.close('all')

def produce_scaled_fts(ticnum,lc):
    print(f"making data/TESS_plots/scaled_FTs/{ticnum}.png")
    p = tf.query(f"TIC=={ticnum}")["P"].values[0]
    if p < 10:
        fmax = 8/p
    else:
        fmax = 10
    fig = lc.to_periodogram(maximum_frequency=fmax).plot()
    plt.axvline(1.0/p,color='r', ls='--', lw=0.8)
    plt.xlim(0,fmax)
    plt.ylim(bottom=0)
    plt.savefig(f"data/TESS_plots/scaled_FTs/{ticnum}.png",bbox_inches='tight')
    plt.clf()
    plt.close('all')

# (Re-)Produce the plots and save local files if the variable below is set to True
produce_plots = True
if produce_plots:
    save_fits_files_locally(files)
    for t in tqdm(tf["TIC"].values):
        try:
            lc = get_lightcurve(t)
        except:
            print(f"Could not retrieve lightcurve for TIC{t}.")
        try:
            save_lc(t,lc)
        except:
            print(f"TIC{t} lc save failed.")
        try:
            produce_lks(t,lc)
        except:
            print(f"TIC{t} lk plot failed.")
        try:
            produce_fts(t,lc)
        except:
            print(f"TIC{t} ft plot failed.")
        try:
            produce_scaled_fts(t,lc)
        except:
            print(f"TIC{t} scaled ft plot failed.")
        try:
            produce_folded_lks(t,lc)
        except:
            print(f"TIC{t} folded lk plot failed.")

