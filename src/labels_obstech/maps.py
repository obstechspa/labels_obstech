from labels_obstech import *
from astropy.table import Table
from math import cos, sin, pi, sqrt

import matplotlib
matplotlib.use('pgf')
from matplotlib import pylab as plt
matplotlib.rcParams['pgf.preamble'] = r'\usepackage{hyperref} \hypersetup{colorlinks=true,urlcolor=red}'
matplotlib.rcParams['pgf.texsystem'] = 'pdflatex'

from .utils import download_sheet

def building_map(buildings: Table, telescopes: Table, building: str) -> None:

    fig = plt.figure(2, figsize=(8.5, 11))
    fig.clf()
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1, 3])
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')

    queue_url = 'https://obstech.org/helpdesk/scp/tickets.php?queue={queue}'

    # Plot general map highlighting the building
   
    tab = buildings 
    lat = tab['lat'].mean()

    for row in tab:
        
        x0, y0, x, y = row['X0'], row['Y0'], row['X'], row['Y']

        color = 'k' if row['Building'] != 'main' else 'b'
        if row['Building'] == str(building):
            color = 'r'
            width, depth = x, y
            door_x1, door_x2 = row['x1'], row['x2']
            angle = row['angle']
            queue = row['queue'] 
        if row['shape'] == 'rect':
            artist = plt.Rectangle(
                    (x0, y0), x, y, angle=row['angle'], color=color
               )
        else:
            artist = plt.Circle((x0, y0), x/2, color=color)
        ax1.add_artist(artist)

    ax1.set_ylim(-20, max(tab['Y0']) + 20)
    ax1.set_xlim(-15, max(tab['X0']) + 15)
    ax1.axis('off')

    # dowload telescope list
    tab = telescopes

    s = tab['status']
    b = tab['building']
    tab = tab[(b == str(building)) & ((s == 'empty') | (s ==  'active'))]

    # building outline

    ax2.plot(
        [door_x2, width, width,     0, 0, door_x1], 
        [0,       0,     depth, depth, 0,       0], 
        'k-'
    )

    lat = lat * pi / 180
    angle = angle * pi / 180 

    for row in tab:
    
        # pier position

        x, y, d = float(row['x']), float(row['y']), float(row['d'])
        if row['section'] == 'disk':
            artist = plt.Circle((x, y), d/2, color=(.5,.5,.5))
        else:
            artist = plt.Rectangle((x - d/2, y - d/2), d, d, color=(.5,.5,.5))
        ax2.add_artist(artist)

        if row['status'] == 'empty':
            continue

        # telescope turn radius

        L, l, r = float(row['L']), float(row['l']), float(row['r'])
        Lh = L * cos(lat)
        lh = -l * sin(lat)
        
        mount = row['type']

        if 'EQ' in mount:
            x1 = x - (Lh - lh) * cos(angle - pi/2)
            y1 = y + (Lh - lh) * sin(angle - pi/2) 
        else:
            x1 = x
            y1 = y
            r = sqrt(r**2 + l**2)

        if mount == '2xF/AZ':
            for li in [-L, L]:
                circle = plt.Circle((x1, y1 + li), r, color='g', alpha=.3) 
                ax2.add_artist(circle)
        else:
            circle = plt.Circle((x1, y1), r, color='g', alpha=.3)
            ax2.add_artist(circle)

        kw = dict(va='center', ha='center', fontsize=12)
        kw2 = dict(va='center', ha='center', fontsize=8)
        hwid = row['HWID']
        url = queue_url.format(queue=row['queue'])
        hwid = f"\\href{{{url}}}{{{hwid}}}"

        owner = row['owner']
        if row['section'] == 'disk':
            dist = -0.15 if angle < 0 else 0.35
            dist2 = dist + 0.15
            ax2.text(x1, y1 - d/2 - 0.2, hwid, **kw)
            ax2.text(x1, y1 - d/2 - 0.4, owner, **kw2)
        else:
            ax2.text(x, y - d/2 - 0.2, hwid, **kw) 
            ax2.text(x, y - d/2 - 0.4, owner, **kw2)

    if int(building) == 6:
        y0 = 7*1.22 + .65
        dy = depth - y0
        rect = plt.Rectangle((0, y0), width, dy, color='y')
        ax2.add_artist(rect)
        ax2.text(width/2, y0 + dy/2, 'ExoAnalytics', **kw)

    ax2.axis('off')
    ax2.set_ylim(-0.2, 14.42 +0.2)
    fig.subplots_adjust(
        left=0.005, right=.995,bottom=0.005, top=.995,
        wspace=.005
    )
        
    url = f'https://obstech.org/helpdesk/scp/tickets.php?queue={queue}'
    fig.suptitle(f'\\href{{{url}}}{{Building {building}}}', fontsize=16)

    fig.savefig(f'building-{int(building):02}-map.pdf')

def make_building_maps() -> None:

    sheet_id = '1rgqsUifjIKhl6pXm7DFsNiQsGiZKPDvuPoQ98Z6DuKc'

    # Building list

    range_name = "Building queues!A2:K"
    values = download_sheet(sheet_id, range_name)
    tab = Table(rows=values[1:], names=values[0])
    tab = tab[tab['lat'] != '']
    tab = Table(tab, dtype=(str,)*4 + (float,)*7)
   
        # transform (lat, lon) into (X, Y) position
 
    lat = tab['lat'].mean()
    Y0 =  (tab['lat'] - min(tab['lat'])) / 90 * 1e7
    X0 =  (tab['lon'] - min(tab['lon'])) / 90 * 1e7 * cos(180 / pi * lat)
    tab.add_column(X0, name='X0')
    tab.add_column(Y0, name='Y0')
        
    buildings = tab
   
    # Telescope list
 
    range_name = "Telescope queues!A2:O"
    values = download_sheet(sheet_id, range_name)
    tab = Table(rows=values[1:], names=values[0])

    telescopes = tab

    # Building map and location

    for building in range(1, 12):
        building_map(buildings, telescopes, building)
