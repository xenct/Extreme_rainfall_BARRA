#barplot of costs

plt.figure(figsize=(4,3))
plt.bar([0.5, 1.5, 2.5, 3.5, 4.5], [350, 340, 240, 70, 1], 0.7, tick_label = ["Flood","Bushfire", "Hail", "Storm", "Cyclone"], color = 'skyblue')
plt.title("Insurance cost of natural disasters\nVictoria 2017")
plt.ylabel("Millions of dollars")
plt.ylim(0,400)
plt.tight_layout(pad=1)

#plt.savefig("/home/563/gt3409/Documents/Storm_cost_plt.png")
