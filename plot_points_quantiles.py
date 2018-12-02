# The aim of this script is to  compare the extreme values for each station as determined by BARRA, AWS, and AWAP


# for each station

# for each of AWAP, AWS, BARRA
plt.figure(figsize=(8,4))
for i in range(len(station_ids)):
    ID = station_ids[i]
    for stat in ['95p', '99p', 'max']:
        plt.scatter(x = 4*i+1.3, y=AWAP_stats_df[stat][ID], marker = '_', color='grey')
        plt.scatter(x = 4*i+2, y=AWS_stats_df[stat][ID], marker = '_', color='k')
        plt.scatter(x = 4*i+2.7, y=BARRA_stats_df[stat][ID], marker = '_', color='b')
    plt.vlines(x=4*i+1.3, ymin=AWAP_stats_df['95p'][ID], ymax=AWAP_stats_df['max'][ID], lw=0.5, color = 'grey')
    plt.vlines(x=4*i+2, ymin=AWS_stats_df['95p'][ID], ymax=AWS_stats_df['max'][ID], lw=0.5, color = 'k')
    plt.vlines(x=4*i+2.7, ymin=BARRA_stats_df['95p'][ID], ymax=BARRA_stats_df['max'][ID], lw=0.5, color = 'b')
plt.legend(["AWAP", "AWS", "BARRA"])
plt.ylim((0,170))
plt.xticks([4*x+2 for x in range(13)], station_ids, rotation =-90)
plt.ylabel("Daily precipitation (mm)")
plt.xlabel("Station ID")
plt.title("Comparison of Extreme Statistics\n95p, 99p, max")
plt.tight_layout()
#plt.savefig("/home/563/gt3409/Documents/images/Extreme_stats.png")
plt.show()



plt.figure(figsize=(8,4))
for i in range(len(station_ids)):
    ID = station_ids[i]
    for stat in ['R95pTOT', 'R99pTOT', 'PRCPTOT']:
        plt.scatter(x = 4*i+1.3, y=AWAP_stats_df[stat][ID], marker = '_', color='grey')
        plt.scatter(x = 4*i+2, y=AWS_stats_df[stat][ID], marker = '_', color='k')
        plt.scatter(x = 4*i+2.7, y=BARRA_stats_df[stat][ID], marker = '_', color='b')
    plt.vlines(x=4*i+1.3, ymin=AWAP_stats_df['R99pTOT'][ID], ymax=AWAP_stats_df['PRCPTOT'][ID], lw=0.5, color = 'grey')
    plt.vlines(x=4*i+2, ymin=AWS_stats_df['R99pTOT'][ID], ymax=AWS_stats_df['PRCPTOT'][ID], lw=0.5, color = 'k')
    plt.vlines(x=4*i+2.7, ymin=BARRA_stats_df['R99pTOT'][ID], ymax=BARRA_stats_df['PRCPTOT'][ID], lw=0.5, color = 'b')
plt.legend(["AWAP", "AWS", "BARRA"])
plt.ylim((0,2000))
plt.xticks([4*x+2 for x in range(13)], station_ids, rotation =-90)
plt.ylabel("Annual precipitation (mm)")
plt.xlabel("Station ID")
plt.title("Comparison of Extreme Statistics\nR99pTOT, R95pTOT, PRCPTOT")
plt.tight_layout()
#plt.savefig("/home/563/gt3409/Documents/images/Extreme_stats_annual_tots.png")
plt.show()
