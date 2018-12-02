import matplotlib.colors as colors

def map_season_prcp(DJF, MAM, JJA, SON, lats, lons, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", AWAP_ann = prcp_data['AWAP_ann'], norm = BoundaryNorm(levels['year'], len(levels['year'])-1), cmap_extend = "max"):
    seasons = [DJF, MAM, JJA, SON]
    season_title = ['DJF', 'MAM', 'JJA', 'SON']
    fig = plt.figure()
    for i, data in zip(range(4), seasons):
        ax = fig.add_subplot(2,2,i+1, projection=projection)
        ax.set_extent(latlonbox) 
        #data[AWAP_ann<1]=0
        im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
#        ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
        ax.coastlines('10m')
        plt.title(f"{season_title[i]}")
    ax = fig.add_axes([0,0,1.1,1], visible = False) #[left, bottom, width, height]
    plt.subplots_adjust(right = 0.85)
    if cmap_extend == "max":
        cbar_ticks = levels[:-1]
    else: # if cbar_ticks == "both"
        cbar_ticks = levels[:]
    cbar = plt.colorbar(im, ticks = cbar_ticks, shrink = 0.6, extend = cmap_extend, fraction = 0.2)
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.suptitle(title)
    return


jja_r95ptot_diff = r95ptot(prcp_data['BARRA_JJA'],prcp_data['AWAP_ann']) - r95ptot(prcp_data['AWAP_JJA'],prcp_data['AWAP_ann'])

son_r95ptot_diff = r95ptot(prcp_data['BARRA_SON'],prcp_data['AWAP_ann']) - r95ptot(prcp_data['AWAP_SON'],prcp_data['AWAP_ann'])

djf_r95ptot_diff = r95ptot(prcp_data['BARRA_DJF'],prcp_data['AWAP_ann']) - r95ptot(prcp_data['AWAP_DJF'],prcp_data['AWAP_ann'])

mam_r95ptot_diff = r95ptot(prcp_data['BARRA_MAM'],prcp_data['AWAP_ann']) - r95ptot(prcp_data['AWAP_MAM'],prcp_data['AWAP_ann'])


edge = 100
map_season_prcp(djf_r95ptot_diff,
                mam_r95ptot_diff,
                jja_r95ptot_diff,
                son_r95ptot_diff,
                AWAP_lats,
                AWAP_lons,
                cmap = cm.get_cmap(cmap_custom_RdBu),
                norm = colors.Normalize(vmin=-1*edge, vmax=edge),
                cmap_extend = "both",
                levels = np.arange(-1*edge, edge * 1.1, 2*edge/10),
                title = f"BARRA-AWAP R95PTOT\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP")


jja_r95ptot_ratio = r95ptot(prcp_data['BARRA_JJA'],prcp_data['AWAP_ann']) / r95ptot(prcp_data['AWAP_JJA'],prcp_data['AWAP_ann'])
jja_r95ptot_ratio =jja_r95ptot_ratio*(AWAPmax>1)

son_r95ptot_ratio = r95ptot(prcp_data['BARRA_SON'],prcp_data['AWAP_ann']) / r95ptot(prcp_data['AWAP_SON'],prcp_data['AWAP_ann'])
son_r95ptot_ratio = son_r95ptot_ratio*(AWAPmax>1)

djf_r95ptot_ratio = r95ptot(prcp_data['BARRA_DJF'],prcp_data['AWAP_ann']) / r95ptot(prcp_data['AWAP_DJF'],prcp_data['AWAP_ann'])
djf_r95ptot_ratio = djf_r95ptot_ratio*(AWAPmax>1)

mam_r95ptot_ratio = r95ptot(prcp_data['BARRA_MAM'],prcp_data['AWAP_ann']) / r95ptot(prcp_data['AWAP_MAM'],prcp_data['AWAP_ann'])
mam_r95ptot_ratio = mam_r95ptot_ratio*(AWAPmax>1)

map_season_prcp(djf_r95ptot_ratio,
                mam_r95ptot_ratio,
                jja_r95ptot_ratio,
                son_r95ptot_ratio,
                AWAP_lats,
                AWAP_lons,
                cmap = cm.get_cmap(cmap_custom_RdBu),
                norm = BoundaryNorm(list(np.arange(0,1,0.1))+list(np.arange(1,11,1)), 21),
                cmap_extend = "both",
                levels = list(np.arange(0,1,0.1))+list(np.arange(1,11,1)),
                title = f"BARRA-AWAP R95PTOT\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP")
plt.show()



jja_r20mm_diff = (r20mm(prcp_data['BARRA_JJA']) - r20mm(prcp_data['AWAP_JJA']))/6
son_r20mm_diff = (r20mm(prcp_data['BARRA_SON']) - r20mm(prcp_data['AWAP_SON']))/6
djf_r20mm_diff = (r20mm(prcp_data['BARRA_DJF']) - r20mm(prcp_data['AWAP_DJF']))/6
mam_r20mm_diff = (r20mm(prcp_data['BARRA_MAM']) - r20mm(prcp_data['AWAP_MAM']))/6

custom_RdBu_centred = cm.get_cmap("RdBu",11)(np.arange(11))
custom_RdBu_centred[5] = [1,1,1,1]
cmap_custom_RdBu_centred = LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu_centred, 11) 

map_season_prcp(djf_r20mm_diff,
                mam_r20mm_diff,
                jja_r20mm_diff,
                son_r20mm_diff,
                AWAP_lats,
                AWAP_lons,
                cmap =cmap_custom_RdBu_centred ,
                norm = BoundaryNorm(np.arange(-5.5,6,1), 11),
                cmap_extend = "both",
                levels = np.arange(-5,6,1),
                title = f"BARRA-AWAP R20mm\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP (days per season)")
#plt.savefig("Documents/images/season_AWAP_BARRA_r20mm_diff_2010-2015.png") 



custom_RdBu_21 = cm.get_cmap("RdBu",21)(np.arange(21))
custom_RdBu_21[10] = [1,1,1,1]
cmap_custom_RdBu_21 = LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu_21, 21) 


jja_r10mm_diff = (r10mm(prcp_data['BARRA_JJA']) - r10mm(prcp_data['AWAP_JJA']))/6
son_r10mm_diff = (r10mm(prcp_data['BARRA_SON']) - r10mm(prcp_data['AWAP_SON']))/6
djf_r10mm_diff = (r10mm(prcp_data['BARRA_DJF']) - r10mm(prcp_data['AWAP_DJF']))/6
mam_r10mm_diff = (r10mm(prcp_data['BARRA_MAM']) - r10mm(prcp_data['AWAP_MAM']))/6


map_season_prcp(djf_r10mm_diff,
                mam_r10mm_diff,
                jja_r10mm_diff,
                son_r10mm_diff,
                AWAP_lats,
                AWAP_lons,
                cmap =cmap_custom_RdBu_21,
                norm = BoundaryNorm(np.arange(-10.5,11,1), 21),
                cmap_extend = "both",
                levels = np.arange(-10,11,1),
                title = f"BARRA-AWAP R10mm\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP (days per season)")
#plt.savefig("Documents/images/season_AWAP_BARRA_r10mm_diff_2010-2015.png") 





 
