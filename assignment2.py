import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from helper import create_plot
from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES

def read_countries_data(countries_csv_name):
    return pd.read_csv(countries_csv_name)

def create_sample_population(countries_data, countries, sample_ratio):
    sample_population = []
    for country in countries:
        country_data = countries_data[countries_data['country'] == country].iloc[0]
        population = int(country_data['population'] / sample_ratio)
        for age_group in ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']:
            group_size = int(population * country_data[age_group] / 100)
            sample_population.extend([
                {'person_id': len(sample_population) + i, 'age_group_name': age_group, 'country': country}
                for i in range(group_size)
            ])
    return pd.DataFrame(sample_population)

def simulate_infection(person, start_date, end_date):
    timeline = []
    current_state = 'H'
    prev_state = None
    current_date = start_date
    staying_days = 0
    
    while current_date <= end_date:
        if staying_days >= HOLDING_TIMES[person['age_group_name']][current_state]:
            transition_probs = TRANSITION_PROBS[person['age_group_name']][current_state]
            new_state = np.random.choice(list(transition_probs.keys()), p=list(transition_probs.values()))
            if new_state != current_state:
                staying_days = 0
                prev_state = current_state
                current_state = new_state
        
        timeline.append({
            'person_id': person['person_id'],
            'age_group_name': person['age_group_name'],
            'country': person['country'],
            'date': current_date.strftime('%Y-%m-%d'),
            'state': current_state,
            'staying_days': staying_days,
            'prev_state': prev_state
        })
        
        current_date += timedelta(days=1)
        staying_days += 1
    
    return timeline

def run_simulation(sample_population, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_timelines = []
    for _, person in sample_population.iterrows():
        all_timelines.extend(simulate_infection(person, start_date, end_date))
    
    return pd.DataFrame(all_timelines)

def summarize_results(simulated_timeseries):
    summary = simulated_timeseries.groupby(['date', 'country', 'state']).size().unstack(fill_value=0).reset_index()
    summary = summary.rename(columns={'H': 'H', 'I': 'I', 'S': 'S', 'M': 'M', 'D': 'D'})
    return summary

def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    # Read countries data
    countries_data = read_countries_data(countries_csv_name)
    
    # Create sample population
    sample_population = create_sample_population(countries_data, countries, sample_ratio)
    
    # Run simulation
    simulated_timeseries = run_simulation(sample_population, start_date, end_date)
    
    # Save simulated timeseries (now including prev_state)
    simulated_timeseries.to_csv('a2-covid-simulated-timeseries.csv', index=False)
    
    # Summarize results
    summary = summarize_results(simulated_timeseries)
    
    # Save summary
    summary.to_csv('a2-covid-summary-timeseries.csv', index=False)
    
    # Create plot
    create_plot('a2-covid-summary-timeseries.csv', countries)

if __name__ == "__main__":
    # This section can be used for testing the implementation
    run(countries_csv_name='a2-countries.csv', 
        countries=['Afghanistan', 'Sweden', 'Japan'], 
        sample_ratio=1e6, 
        start_date='2021-04-01', 
        end_date='2022-04-30')