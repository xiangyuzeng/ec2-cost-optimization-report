#!/usr/bin/env python3
"""Generate visualizations for 21st & 3rd store opening analysis"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import csv

# Read daily data
daily_data = []
with open('/app/21st_3rd_daily_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        daily_data.append(row)

dates = [row['Date'][-5:] for row in daily_data]  # MM-DD format
days_of_week = [row['Day_of_Week'][:3] for row in daily_data]  # Mon, Tue, etc.
cup_counts = [int(row['Cup_Count']) for row in daily_data]

# Chart 1: Daily Traffic Line Chart
plt.figure(figsize=(12, 7))
plt.plot(range(len(cup_counts)), cup_counts, marker='o', markersize=12,
         linewidth=3, color='#FF6B35', alpha=0.8)

# Highlight opening day
plt.scatter([0], [cup_counts[0]], s=300, color='#FF6B35',
            edgecolors='black', linewidths=3, zorder=5, alpha=0.9,
            label='Opening Day (Half-day)')

# Add value labels on points
for i, (count, day) in enumerate(zip(cup_counts, days_of_week)):
    plt.text(i, count + 15, f'{count}\n{day}',
             ha='center', fontsize=10, fontweight='bold')

# Add horizontal lines for averages
weekday_avg = sum([cup_counts[i] for i in [3, 4, 5]]) / 3  # Mon, Tue, Wed
plt.axhline(y=weekday_avg, color='green', linestyle='--', linewidth=2,
            alpha=0.5, label=f'Weekday Avg: {weekday_avg:.0f} cups')

weekend_avg = sum([cup_counts[1], cup_counts[2]]) / 2  # Sat, Sun
plt.axhline(y=weekend_avg, color='blue', linestyle='--', linewidth=2,
            alpha=0.5, label=f'Weekend Avg: {weekend_avg:.0f} cups')

plt.xlabel('Day Number (0 = Opening Day)', fontsize=13, fontweight='bold')
plt.ylabel('Drink Cups per Day', fontsize=13, fontweight='bold')
plt.title('21st & 3rd Store: Daily Traffic from Opening Day\n(Opened Feb 6, 2026 at 12 PM)',
          fontsize=15, fontweight='bold', pad=20)
plt.legend(fontsize=11, loc='upper right')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(range(len(cup_counts)),
           [f'Day {i}\n{dates[i]}' for i in range(len(dates))],
           fontsize=10)

plt.tight_layout()
plt.savefig('/app/21st_3rd_daily_chart.png', dpi=300, bbox_inches='tight')
print("✓ Chart 1 saved: 21st_3rd_daily_chart.png")
plt.close()

# Chart 2: Hourly Pattern Comparison
# Read hourly data
hourly_data = pd.read_csv('/app/21st_3rd_hourly_data.csv')

# Separate opening day vs subsequent days
opening_day = hourly_data[hourly_data['Date'] == '2026-02-06']
subsequent_weekdays = hourly_data[hourly_data['Date'].isin(['2026-02-09', '2026-02-10', '2026-02-11'])]

# Calculate average for subsequent weekdays by hour
weekday_avg_by_hour = subsequent_weekdays.groupby('Hour')['Cup_Count'].mean()

plt.figure(figsize=(14, 8))

# Plot opening day
hours_opening = opening_day['Hour'].tolist()
cups_opening = opening_day['Cup_Count'].tolist()
plt.bar([h - 0.2 for h in hours_opening], cups_opening, width=0.4,
        label='Opening Day (Feb 6, Fri)', color='#FF6B35', alpha=0.8, edgecolor='black')

# Plot subsequent weekdays average
hours_weekday = weekday_avg_by_hour.index.tolist()
cups_weekday = weekday_avg_by_hour.values.tolist()
plt.bar([h + 0.2 for h in hours_weekday], cups_weekday, width=0.4,
        label='Weekdays Avg (Feb 9-11)', color='#4ECDC4', alpha=0.8, edgecolor='black')

plt.xlabel('Hour of Day', fontsize=13, fontweight='bold')
plt.ylabel('Drink Cups per Hour', fontsize=13, fontweight='bold')
plt.title('21st & 3rd: Hourly Traffic Pattern\nOpening Day vs. Subsequent Weekdays',
          fontsize=15, fontweight='bold', pad=20)
plt.legend(fontsize=11)
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.xticks(range(24), [f'{h}:00' for h in range(24)], rotation=45, ha='right')

# Highlight 4 PM opening day rush
plt.annotate('Opening Rush\n59 cups',
             xy=(16, 59), xytext=(17, 65),
             fontsize=10, ha='left',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
             arrowprops=dict(arrowstyle='->', lw=1.5))

plt.tight_layout()
plt.savefig('/app/21st_3rd_hourly_chart.png', dpi=300, bbox_inches='tight')
print("✓ Chart 2 saved: 21st_3rd_hourly_chart.png")
plt.close()

print("\n" + "="*60)
print("VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*60)
print("\nFiles created:")
print("  1. 21st_3rd_daily_chart.png (Daily traffic line chart)")
print("  2. 21st_3rd_hourly_chart.png (Hourly pattern comparison)")
print("\nCharts ready for presentation! ✓")
