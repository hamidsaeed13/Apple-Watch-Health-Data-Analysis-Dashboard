import os
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np

class AppleWatchData:
    def __init__(self, xml_data_file_path, source_name, tag_name='Record'):
        self.file_path = os.path.expanduser(xml_data_file_path)
        self.source_name = source_name
        self.tag_name = tag_name
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()
        self.records = self.root.findall('.//' + tag_name)
        self.me_element=self.root.find('Me')

    def parse_tag(self, attribute):
        record_list = []
        for s in self.records:
            if s.attrib.get('type') == attribute:
                record_list.append(s)
                # print("Record Found")
        return record_list

    def parse_record(self, record):
        start_timestamp_string = record.attrib.get('startDate')
        end_timestamp_string = record.attrib.get('endDate')
        start_time = datetime.strptime(start_timestamp_string, '%Y-%m-%d %H:%M:%S -0600')
        end_time = datetime.strptime(end_timestamp_string, '%Y-%m-%d %H:%M:%S -0600')
        try:
            biometric = float(record.attrib.get('value'))
        except ValueError:
            biometric = record.attrib.get('value')
        return start_time, end_time, biometric

    def parse_metadata(self, record):
        meta_data = {'bpm': [], 'time': []}
        nodes = record.findall('.//InstantaneousBeatsPerMinute')
        for node in nodes:
            bpm = node.attrib.get('bpm')
            time = node.attrib.get('time')
            if bpm and time:
                meta_data['bpm'].append(bpm)
                meta_data['time'].append(time)
        return meta_data

    def parse_record_list(self, record_list):
        apple_data = [self.parse_record(record) for record in record_list]
        apple_array = np.array(apple_data)
        return apple_array

    def load_heart_rate_data(self):
        attribute = 'HKQuantityTypeIdentifierHeartRate'
        record_list = self.parse_tag(attribute)
        hr_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        hr_data_df['start_timestamp'] = apple_array[:, 0]
        hr_data_df['end_timestamp'] = apple_array[:, 1]
        hr_data_df['heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        hr_data_df.sort_values('start_timestamp', inplace=True)

        return hr_data_df

    def load_heart_rate_variability_data(self):
        attribute = 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN'
        record_list = self.parse_tag(attribute)
        hrv_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        instantaneous_bpm = [self.parse_metadata(record) for record in record_list]

        hrv_data_df['start_timestamp'] = apple_array[:, 0]
        hrv_data_df['end_timestamp'] = apple_array[:, 1]
        hrv_data_df['heart_rate_variability'] = pd.to_numeric(apple_array[:, 2], errors='ignore')
        hrv_data_df['instantaneous_bpm'] = instantaneous_bpm

        return hrv_data_df

    def load_resting_heart_rate_data(self):
        attribute = 'HKQuantityTypeIdentifierRestingHeartRate'
        record_list = self.parse_tag(attribute)
        resting_hr_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        resting_hr_data_df['start_timestamp'] = apple_array[:, 0]
        resting_hr_data_df['end_timestamp'] = apple_array[:, 1]
        resting_hr_data_df['resting_heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        resting_hr_data_df.sort_values('start_timestamp', inplace=True)

        return resting_hr_data_df

    def load_walking_heart_rate_data(self):
        attribute = 'HKQuantityTypeIdentifierWalkingHeartRateAverage'
        record_list = self.parse_tag(attribute)
        walking_hr_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        print(apple_array)
        walking_hr_data_df['start_timestamp'] = apple_array[:, 0]
        walking_hr_data_df['end_timestamp'] = apple_array[:, 1]
        walking_hr_data_df['walking_heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        walking_hr_data_df.sort_values('start_timestamp', inplace=True)

        return walking_hr_data_df

    def load_distance_data(self):
        attribute = 'HKQuantityTypeIdentifierDistanceWalkingRunning'
        record_list = self.parse_tag(attribute)
        distance_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        distance_data_df['start_timestamp'] = apple_array[:, 0]
        distance_data_df['end_timestamp'] = apple_array[:, 1]
        distance_data_df['distance_walk_run'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return distance_data_df

    def load_basal_energy_data(self):
        attribute = 'HKQuantityTypeIdentifierBasalEnergyBurned'
        record_list = self.parse_tag(attribute)
        energy_burned_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        energy_burned_data_df['start_timestamp'] = apple_array[:, 0]
        energy_burned_data_df['end_timestamp'] = apple_array[:, 1]
        energy_burned_data_df['energy_burned'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return energy_burned_data_df

    def load_stand_hour_data(self):
        attribute = 'HKCategoryTypeIdentifierAppleStandHour'
        record_list = self.parse_tag(attribute)
        stand_hour_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        stand_hour_df['start_timestamp'] = apple_array[:, 0]
        stand_hour_df['end_timestamp'] = apple_array[:, 1]
        stand_hour_df['stand_hour'] = apple_array[:, 2]

        new_labels = {'HKCategoryValueAppleStandHourIdle': 'Idle',
                       'HKCategoryValueAppleStandHourStood': 'Stood'}
        stand_hour_df['stand_hour'] = stand_hour_df['stand_hour'].replace(new_labels)

        return stand_hour_df

    def load_step_data(self):
        attribute = 'HKQuantityTypeIdentifierStepCount'
        record_list = self.parse_tag(attribute)
        step_data_df = pd.DataFrame()

        apple_array = self.parse_record_list(record_list)
        step_data_df['start_timestamp'] = apple_array[:, 0]
        step_data_df['end_timestamp'] = apple_array[:, 1]
        step_data_df['steps'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return step_data_df

    def load_Personal_data(self):
        records = []

        # Extract user information
        me_data = {}
        for key, value in self.me_element.attrib.items():
            clean_key = key.replace("HKCharacteristicTypeIdentifier", "")
            me_data[clean_key] = value.replace("HKBiologicalSex", "").replace("HKBloodType", "").replace("HKFitzpatrickSkinType", "")



        # Extract height data
        attribute = 'HKQuantityTypeIdentifierHeight'
        record_list = self.parse_tag(attribute)
        if record_list:
            me_data['UserName'] = record_list[0].attrib['sourceName']
        # Append user data to records
        records.append(me_data)     
        if record_list:
            record_data = {
                'type': record_list[0].attrib['type'].replace("HKQuantityTypeIdentifier", ""),
                'unit': record_list[0].attrib['unit'],
                'creationDate': record_list[0].attrib.get('creationDate', ''),
                'startDate': record_list[0].attrib['startDate'],
                'endDate': record_list[0].attrib['endDate'],
                'value': record_list[0].attrib['value']
            }
            records.append(record_data)

        # Extract body mass data
        attribute = 'HKQuantityTypeIdentifierBodyMass'
        record_list = self.parse_tag(attribute)
        if record_list:
            record_data = {
                'type': record_list[0].attrib['type'].replace("HKQuantityTypeIdentifier", ""),
                'unit': record_list[0].attrib['unit'],
                'creationDate': record_list[0].attrib.get('creationDate', ''),
                'startDate': record_list[0].attrib['startDate'],
                'endDate': record_list[0].attrib['endDate'],
                'value': record_list[0].attrib['value']
            }
            records.append(record_data)

        return records
