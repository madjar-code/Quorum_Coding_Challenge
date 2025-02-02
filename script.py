import pandas as pd
from pandas import DataFrame


def generate_legislator_report(
    votes: DataFrame,
    vote_results: DataFrame,
    legislators: DataFrame
) -> None:
    vote_data: DataFrame = votes.merge(
        vote_results,
        left_on='id',
        right_on='vote_id'
    )

    legislator_votes: DataFrame = vote_data.groupby(
        ['legislator_id', 'vote_type']
    )['bill_id'].count().unstack(fill_value=0)
    legislator_votes.columns = [
        'num_opposed_bills',
        'num_supported_bills'
    ]
    legislator_votes = legislator_votes.reset_index()
    legislator_report: DataFrame = legislator_votes.merge(
        legislators[['id', 'name']],
        right_on='id',
        left_on='legislator_id',
    )
    legislator_report.to_csv(
        'legislators-support-oppose-count.csv',
        index=False,
    )


if __name__ == "__main__":
    bills: DataFrame = pd.read_csv('bills.csv')
    votes: DataFrame = pd.read_csv('votes.csv')
    vote_results: DataFrame = pd.read_csv('vote_results.csv')
    legislators: DataFrame = pd.read_csv('legislators.csv')

    generate_legislator_report(votes, vote_results, legislators)

    print('CSV file generated successfully!')
