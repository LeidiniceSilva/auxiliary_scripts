# -*- coding: utf-8 -*-

__author__ = "Leidinice Silva"
__copyright__ = "Copyright 2016, Funceme Hydropy Project"
__credits__ = ["Francisco Vasconcelos Junior", "Marcelo Rodrigues"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Marcelo Rodrigues"
__email__ = "leidinice.silvae@funceme.br"
__date__ = 07/25/2016


# Import Datas
import netCDF4
import matplotlib as mpl ; mpl.use('Agg')  # Descomente para não mostrar a janela em cada plot
import re
import wget
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy.ma as ma
import scipy.stats as st
from PyFuncemeClimateTools import DefineGrid as Dg
from PyFuncemeClimateTools import PlotMaps as pm


def caso_shape(data, lat, lon, shp):

    shapeurl = "http://opendap2.funceme.br:8001/data/utils/shapes/regioes/{0}".format(shp)
    line = re.sub('[/]', ' ', shapeurl); line = line.split(); Ptshape = '/tmp/' + line[-1]; shpn = line[-2].title()
    if not os.path.exists(Ptshape): Ptshape = wget.download(shapeurl, '/tmp', bar=None)

    xy = np.loadtxt(Ptshape)
    xx = xy[:, 0]
    yy = xy[:, 1]

    plt.plot(xx, yy, color='k', linewidth=0.5)
    plt.show()
    plt.savefig('Contorno_{0}.png'.format(shpn))
    # plt.close()

    shpn  = line[-2].title()

    # Quando lon de 0:360 mudando para -180:180
    if not np.any(lon < 0): lon=np.where(lon > 180, lon-360, lon)

    # PONTOS DO POLIGONO QUE SERA MASCARADO
    Ptsgrid, lonlatgrid, Ptmask = Dg.pointinside(lat, lon, shapefile=Ptshape)

    # APLICANDO MASCARA DO POLIGONO NO DADO DE ENTRADA
    VarMasked_data = np.ma.array(data[:, :, :], mask=np.tile(Ptmask, (data.shape[0], 1))) # Array mascarada!!!

    return VarMasked_data


def caso_shape_so_plot(shp):

    shapeurl = "http://opendap2.funceme.br:8001/data/utils/shapes/{0}".format(shp)
    line = re.sub('[/]', ' ', shapeurl); line = line.split(); Ptshape = '/tmp/' + line[-1]; shpn = line[-2].title()
    if not os.path.exists(Ptshape): Ptshape = wget.download(shapeurl, '/tmp', bar=None)

    xy = np.loadtxt(Ptshape)
    xx = xy[:, 0]
    yy = xy[:, 1]

    plt.plot(xx, yy, color='k', linewidth=0.5)
    plt.show()


def txtbox(text, xpos, ypos, fontsize, (col, lin, pos)):
    txtsp = plt.subplot(col, lin, pos)
    txt = text
    props = dict(boxstyle='round', facecolor='wheat', alpha=0)
    txtsp.text(xpos, ypos, txt, transform=txtsp.transAxes, fontsize=fontsize, verticalalignment='top', bbox=props)

# Directories of input and output data

path_in = "/home/leidinice/Documentos/esi/dados/esi/clim/4WK/"

mes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
dic_esi = {'Jan': 3, 'Fev': 7, 'Mar': 12, 'Abr': 16, 'Mai': 20, 'Jun': 25, 'Jul': 29, 'Ago': 34, 'Set': 38,
           'Out': 42, 'Nov': 47, 'Dez': 51}

ANOS = range(2015, 2016 + 1)
qnt_anos = len(ANOS)

for i, ANO in enumerate(ANOS):

    print "ANO>", ANO

    name = 'esi_4WK_SMN_{0:4d}_SA.nc'.format(ANO)
    data = netCDF4.Dataset(str(path_in) + name)
    esi = data.variables['esi'][:]
    lat = data.variables['latitude'][:]  # Declaring latitude
    lon = data.variables['longitude'][:]  # Declaring longitude

    min_lat, min_lon, min_lat_index, min_lon_index = Dg.gridpoint(lat, lon, -20., -50.0)
    max_lat, max_lon, max_lat_index, max_lon_index = Dg.gridpoint(lat, lon, 0., -34.)
    lats = lat[min_lat_index:max_lat_index]
    lons = lon[min_lon_index:max_lon_index]

    if ANO == ANOS[0]:
        mensal = np.full((qnt_anos * 12, lat.shape[0], lon.shape[0]), np.nan)

    for k in range(0, 12):

        print "MES>", k, mes[k]
        try:

            aux = esi[dic_esi[mes[k]], min_lat_index:max_lat_index, min_lon_index:max_lon_index]
            aux = np.expand_dims(aux, axis=0)
            aux = ma.masked_where(aux <= -6., aux)
            aux = ma.masked_where(aux >= 6., aux)
            mensal[k + i*12, :, :] = aux[:, :]

        except:
            print "Dados faltando. Assumindo NAN."

# making the difference

print mensal.shape

diff = np.full((mensal.shape[0]-1, lat.shape[0], lon.shape[0]), np.nan)

for m in range(mensal.shape[0]-1):

    diff[m, :, :] = mensal[m+1, :, :] - mensal[m, :, :]

y1, y2, x1, x2 = -20., 0., -50., -34.
cor1 = ('#750000', '#ff0000', '#ff8000', '#fcd17d', '#ffff00', '#ffffff', '#00ffff', '#7dd1fa', '#0080ff', '#0000ff', '#000075')  # Paleta
lev1 = (-2., -1.6, -1.3, -0.8, -0.5, 0.5, 0.8, 1.3, 1.6, 2.)

cont = 0

for i, ANO in enumerate(ANOS):

    if ANO == ANOS[0]:

        # CASOS [M+1]-[M]

        for MES in range(12-1):

            # diff[cont, :, :] --> fev2015 - jan2015
            figou1 = 'diff_4WK_{0}_{2}_{1}_{2}.png'.format(mes[MES+1], mes[MES], ANO)
            title1 = u'Variação da Anomalia de ESI \n{0}/{2} - {1}/{2}'.format(mes[MES + 1], mes[MES], ANO)

            print figou1, title1

            fig = plt.figure()
            txtbox(u'Fonte: NOAA/ESSIC and USDA-ARS\nElaboração: FUNCEME', 0.46, 0.06, 8, (1, 1, 1))

            Dmasked = caso_shape(diff[:], lats, lons, '/nordeste_do_brasil/nordeste_do_brasil.txt')
            caso_shape_so_plot('/estados/alagoas/alagoas.txt')
            caso_shape_so_plot('/estados/bahia/bahia.txt')
            caso_shape_so_plot('/estados/ceara/ceara.txt')
            caso_shape_so_plot('/estados/maranhao/maranhao.txt')
            caso_shape_so_plot('/estados/paraiba/paraiba.txt')
            caso_shape_so_plot('/estados/pernambuco/pernambuco.txt')
            caso_shape_so_plot('/estados/piaui/piaui.txt')
            caso_shape_so_plot('/estados/rio_grande_do_norte/rio_grande_do_norte.txt')
            caso_shape_so_plot('/estados/sergipe/sergipe.txt')

            pm.plotmap(
                diff[cont, :, :], lats, lons,
                latsouthpoint=y1, latnorthpoint=y2, lonwestpoint=x1, loneastpoint=x2, ocean_mask=1,
                fig_name=figou1, fig_title=title1, barcolor=cor1, barlevs=lev1, barinf='both', barloc='right')

            plt.close('all')
            plt.cla()

            print "CONTA====", cont
            cont += 1

    if ANO != ANOS[0]:

        # CASO JAN-DEZ

        # diff[11 :, :] --> jan2016 - dez2015
        figou1 = 'diff_4WK_{0}_{2}_{1}_{3}.png'.format(mes[0], mes[11], ANO, ANO-1)
        title1 = u'Variação da Anomalia de ESI \n{0}/{2} - {1}/{3}'.format(mes[0], mes[11], ANO, ANO-1)

        fig = plt.figure()
        txtbox(u'Fonte: NOAA/ESSIC and USDA-ARS\nElaboração: FUNCEME', 0.46, 0.06, 8, (1, 1, 1))

        Dmasked = caso_shape(diff[:], lats, lons, '/nordeste_do_brasil/nordeste_do_brasil.txt')
        caso_shape_so_plot('/estados/alagoas/alagoas.txt')
        caso_shape_so_plot('/estados/bahia/bahia.txt')
        caso_shape_so_plot('/estados/ceara/ceara.txt')
        caso_shape_so_plot('/estados/maranhao/maranhao.txt')
        caso_shape_so_plot('/estados/paraiba/paraiba.txt')
        caso_shape_so_plot('/estados/pernambuco/pernambuco.txt')
        caso_shape_so_plot('/estados/piaui/piaui.txt')
        caso_shape_so_plot('/estados/rio_grande_do_norte/rio_grande_do_norte.txt')
        caso_shape_so_plot('/estados/sergipe/sergipe.txt')

        pm.plotmap(
            diff[cont, :, :], lats, lons,
            latsouthpoint=y1, latnorthpoint=y2, lonwestpoint=x1, loneastpoint=x2, ocean_mask=1,
            fig_name=figou1, fig_title=title1, barcolor=cor1, barlevs=lev1, barinf='both', barloc='right')

        plt.close('all')
        plt.cla()

        print "CONTA====", cont
        cont += 1

        # CASOS [M+1]-[M]

        for MES in range(12-1):

            # diff[cont, :, :] --> fev2015 - jan2015
            figou1 = 'diff_4WK_{0}_{2}_{1}_{2}.png'.format(mes[MES+1], mes[MES], ANO)
            title1 = u'Variação da Anomalia de ESI \n{0}/{2} - {1}/{2}'.format(mes[MES + 1], mes[MES], ANO)

            print
            print figou1, title1

            fig = plt.figure()
            txtbox(u'Fonte: NOAA/ESSIC and USDA-ARS\nElaboração: FUNCEME', 0.46, 0.06, 8, (1, 1, 1))

            Dmasked = caso_shape(diff[:], lats, lons, '/nordeste_do_brasil/nordeste_do_brasil.txt')
            caso_shape_so_plot('/estados/alagoas/alagoas.txt')
            caso_shape_so_plot('/estados/bahia/bahia.txt')
            caso_shape_so_plot('/estados/ceara/ceara.txt')
            caso_shape_so_plot('/estados/maranhao/maranhao.txt')
            caso_shape_so_plot('/estados/paraiba/paraiba.txt')
            caso_shape_so_plot('/estados/pernambuco/pernambuco.txt')
            caso_shape_so_plot('/estados/piaui/piaui.txt')
            caso_shape_so_plot('/estados/rio_grande_do_norte/rio_grande_do_norte.txt')
            caso_shape_so_plot('/estados/sergipe/sergipe.txt')

            pm.plotmap(
                diff[cont, :, :], lats, lons,
                latsouthpoint=y1, latnorthpoint=y2, lonwestpoint=x1, loneastpoint=x2, ocean_mask=1,
                fig_name=figou1, fig_title=title1, barcolor=cor1, barlevs=lev1, barinf='both', barloc='right')

            plt.close('all')
            plt.cla()

            cont += 1



