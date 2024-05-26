from extract_cb_data import get_schedule_cb, get_commentary_cb
from extract_iplt20_data import get_schedule_iplt20, get_commentary_iplt20
from extract_results import get_results_info
from transform_data import extract_data_from_commentary


if __name__ =='__main__':
    # Extract schedule and commentary data from iplt20.com to save it
    df_schedule_ipl, abandoned_matches = get_schedule_iplt20()
    get_commentary_iplt20(df_schedule_ipl, abandoned_matches)
    # Extract schedule and commentary data from cricbuzz.com to save it
    df_schedule_cb = get_schedule_cb()
    get_commentary_cb(df_schedule_cb)
    # Extract results data
    get_results_info()
    # Transformations of data to extract additional iformation and statistics
    extract_data_from_commentary()