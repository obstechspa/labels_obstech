from labels_obstech import *
from astropy.table import Table
from matplotlib import pylab as plt
from math import cos, sin, pi, sqrt

def plot_building(building):

    fig = plt.figure(2, figsize=(8.5, 11))
    fig.clf()
    ax1, ax2 = fig.subplots(1, 2, width_ratios=[1, 3])
    ax1.set_aspect('equal')
    ax2.set_aspect('equal')

    # Read building list

    sheet_id = '1rgqsUifjIKhl6pXm7DFsNiQsGiZKPDvuPoQ98Z6DuKc'
    range_name = "Building queues!A2:K"
    values = download_sheet(sheet_id, range_name)
    tab = Table(rows=values[1:], names=values[0])
    tab = tab[tab['lat'] != '']
    tab = Table(tab, dtype=(str,)*4 + (float,)*7)

    lat = tab['lat'].mean()
    Y0 =  (tab['lat'] - min(tab['lat'])) / 90 * 1e7
    X0 =  (tab['lon'] - min(tab['lon'])) / 90 * 1e7 * cos(180 / pi * lat)
    tab.add_column(X0, name='X0')
    tab.add_column(Y0, name='Y0')

    # Plot general map highlighting the building

    for row in tab:
        
        x0, y0, x, y = row['X0'], row['Y0'], row['X'], row['Y']

        color = 'k'
        if row['Building'] == str(building):
            color = 'r'
            width, depth = x, y
            door_x1, door_x2 = row['x1'], row['x2']
            angle = row['angle']
            print(width, depth, door_x1, door_x2)
 
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

    range_name = "Telescope queues!A2:O"
    values = download_sheet(sheet_id, range_name)
    tab = Table(rows=values[1:], names=values[0])
    tab = tab[(tab['building'] == str(building)) & (tab['status'] == 'active')]
 
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
        if row['section'] == 'disk':
            ax2.text(x1 - 0.35, y1 - 0.35, row['HWID'], **kw, rotation=-45)
        else:
            ax2.text(x, y - d/2 - 0.2, row['HWID'], **kw) 

    ax2.axis('off')
    ax2.set_ylim(-0.2, 14 +0.2)
    fig.subplots_adjust(
        left=0.005, right=.995,bottom=0.005, top=.995,
        wspace=.005
    )
    fig.suptitle(f'Building {building}', fontsize=16)

    fig.savefig(f'building-{building}-map.pdf')

plot_building(8)
plot_building(7)
plot_building(2)
