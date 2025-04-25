import pandas as pd

# Load the data
df = pd.read_csv('olympus-dash/athlete_events.csv')

def test_medal_counting(noc='USA', season='Summer'):
    # Get historical data for the country
    country_data = df[df['NOC'] == noc].copy()
    
    # Filter by season
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]  # Summer Olympics are in years divisible by 4
    else:  # Winter
        country_data = country_data[country_data['Year'] % 4 == 2]  # Winter Olympics are in years divisible by 2 but not 4
    
    # Filter for 2016
    country_data = country_data[country_data['Year'] == 2016]
    
    # Calculate yearly medal counts
    yearly_medals = country_data[country_data['Medal'] != 'None'].groupby(['Year', 'Event', 'Medal']).size().reset_index()
    print("\nMedals by Event and Medal Type for USA in 2016:")
    print(yearly_medals)
    
    yearly_medals = yearly_medals.groupby('Year')['Medal'].count().reset_index()
    yearly_medals.columns = ['Year', 'Medal_Count']
    print("\nTotal Medals for USA in 2016:")
    print(yearly_medals)

if __name__ == "__main__":
    test_medal_counting() 