import logging
import sys
import streamlit as st
import pandas as pd
import os
import glob
from src.global_var import summary_directory, personalization, item_list, load_csv
from src import web_operation
from src import get_set_bid
from src.utils import exist_item_data, list_exist_items, list_exist_items_from_json, display_logs
from src.subscription_check import check_subscription
import subprocess

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
st.set_page_config(layout="wide")
ui_text_df = pd.read_csv('src/language.csv', index_col='id')
lang = 'zhtw'

col1, col2, col3, col4 = st.columns(4)

with col1:
    # check ECOE subscription
    st.header(ui_text_df[lang][0])
    personalization["saa_sub_id"] = st.text_input(
        ui_text_df[lang][1], value=personalization["saa_sub_id"])
    personalization["saa_sub_key"] = st.text_input(
        ui_text_df[lang][2], value=personalization["saa_sub_key"])
    personalization["chrome_profile_data"] = st.text_input(
        ui_text_df[lang][3], value=personalization["chrome_profile_data"])
    personalization["uuid"] = personalization["uuid"] if not pd.isnull(personalization["uuid"]) else subprocess.check_output(
        'wmic csproduct get uuid'.split(), shell=True).decode('utf-8').split()[1]
    st.write(f"{ui_text_df[lang][4]}:{personalization['uuid']}")

    st.header(ui_text_df[lang][5])
    st.write(ui_text_df[lang][6])
    st.write(ui_text_df[lang][7])

    personalization["id"] = st.text_input(
        ui_text_df[lang][8], value=personalization["id"])
    personalization["pwd"] = st.text_input(
        ui_text_df[lang][9], type="password", value=personalization["pwd"])

    save_info_button = st.button(ui_text_df[lang][10])
    if save_info_button:
        personalization_csv = pd.DataFrame(personalization, index=[0])
        personalization_csv.to_csv("personalization.csv", index=False)

    if not check_subscription(personalization):
        st.write(ui_text_df[lang][11])
    else:
        # Shopee account

        login_button = st.button(ui_text_df[lang][12])

        if login_button:
            try:
                driver = web_operation.login()
                driver.quit()
            except:
                st.write(ui_text_df[lang][13])

with col2:
    reload_csv_button = st.button(ui_text_df[lang][27])
    if reload_csv_button:
        load_csv()
    # content for second column
    if check_subscription(personalization):
        st.header(ui_text_df[lang][14])
        st.write(ui_text_df[lang][15])
        edited_df =st.data_editor(item_list, num_rows="dynamic")
        save_item_list_button = st.button(ui_text_df[lang][16])
        if save_item_list_button:
            edited_df.to_csv('item.csv', index=False)

        st.header(ui_text_df[lang][17])
        selected_options = st.multiselect(
            ui_text_df[lang][18], edited_df['item'])

        crawl_data_button = st.button(ui_text_df[lang][19])
        if crawl_data_button and len(selected_options) > 0:
            driver = web_operation.login()
            # driver = web_operation.launchBrowser()
            for selected_item_id_str in selected_options:
                if not exist_item_data(selected_item_id_str):
                    web_operation.crawling_data(driver, selected_item_id_str)
            driver.quit()


with col3:
    if check_subscription(personalization):
        st.header(ui_text_df[lang][20])

        if len(os.listdir(summary_directory)) > 0:
            get_good_bid_button = st.button(ui_text_df[lang][21])
            if get_good_bid_button:
                get_set_bid.get_good_bid_items(item_list)
                st.write("Completed!")

        selected = st.selectbox(
            ui_text_df[lang][22], list_exist_items(summary_directory))

        if selected:
            generate_table_button = st.button(ui_text_df[lang][23])
            if selected and generate_table_button:
                df = pd.DataFrame(list_exist_items_from_json(os.path.join(
                    summary_directory, selected, 'new_keyword_bid.json')))
                edited_df = st.dataframe(df.T)


with col4:
    # content for second column
    if check_subscription(personalization):
        st.header(ui_text_df[lang][24])
        selected_options = st.multiselect(
            ui_text_df[lang][25], item_list['item'], key="set_bid_multiselect")

        if len(selected_options) > 0:
            set_bid_button = st.button(
                ui_text_df[lang][26], key="set_bid_button")
            if set_bid_button and len(selected_options) > 0:
                # driver = web_operation.login()
                driver = web_operation.launchBrowser()
                for i, selected_item_id_str in enumerate(selected_options):

                    # glob all files in the directory
                    items = glob.glob(os.path.join(summary_directory, "*"))
                    items = [
                        item for item in items if selected_item_id_str in item]
                    get_set_bid.set_good_bid_items(items, driver)

                    st.progress((i+1)/len(selected_options))
                    st.info(display_logs())

                driver.quit()
