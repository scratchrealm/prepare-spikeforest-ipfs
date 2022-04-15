import json
import kachery_client as kc
import kachery_cloud as kcl
import yaml


def main():
    x = kcl.load_json('ipfs://bafybeihem5zeyhsgztqzi5o4qvtigsdbelvhw2ssu3x4ve32p2ztf6vq7i?label=spikeforest-sorting-outputs.json')
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    config_nested = {
        'studies': {}
    }
    for s in config['studies']:
        config_nested['studies'][s['study_name']] = {'recording_names': s['recording_names']}
    
    sorting_output_recs = []

    for sorting_output in x:
        study_name = sorting_output['studyName']
        recording_name = sorting_output['recordingName']
        sorter_name = sorting_output['sorterName']
        if study_name in config_nested['studies']:
            if recording_name in config_nested['studies'][study_name]['recording_names']:
                print(study_name, recording_name, sorter_name)
                k = f'spikeforest/{study_name}/{recording_name}/sortingOutput/{sorter_name}'
                sorting_output_rec_uri = kcl.get_mutable(k)
                if sorting_output_rec_uri is not None:
                    try:
                        sorting_output_rec = kcl.load_json(sorting_output_rec_uri)
                    except:
                        sorting_output_rec = None
                else:
                    sorting_output_rec = None
                if sorting_output_rec is None:
                    sorting_output['consoleOut'] = _sha1_to_ipfs_uri(sorting_output['consoleOut'], 'console_out.txt')
                    if 'firings' in sorting_output:
                        sorting_output['firings'] = _sha1_to_ipfs_uri(sorting_output['firings'], 'firings.mda')
                        recording_uri = sorting_output['recordingUri']
                        recording_object = kc.load_json(recording_uri, channel='spikeforest')
                        samplerate = recording_object['params']['samplerate']
                        sorting_output['sortingObject'] = {'firings': sorting_output['firings'], 'samplerate': samplerate}
                    sorting_output_rec = sorting_output
                    kcl.set_mutable(k, kcl.store_json(sorting_output_rec) + f'?label={study_name}.{recording_name}.{sorter_name}.json')
                sorting_output_recs.append(sorting_output_rec)
    sorting_outputs_uri = kcl.store_json({'sortingOutputs': sorting_output_recs}) + '?spikeforest-sorting-outputs.json'
    kcl.set_mutable('spikeforest-sorting-outputs', sorting_outputs_uri)
    print(sorting_outputs_uri)
        
    # recording_records = []
    # for study in config['studies']:
    #     study_set_name = study['study_set_name']
    #     study_name = study['study_name']
    #     for recording_name in study['recording_names']:
    #         print(recording_name)
    #         k = f'spikeforest/{study_name}/{recording_name}/recording'
    #         print(k)
    #         recording_rec_uri = kcl.get_mutable(k)
    #         if recording_rec_uri is not None:
    #             try:
    #                 recording_rec = kcl.load_json(recording_rec_uri)
    #             except:
    #                 print(f'Problem downloading recording record: {recording_rec_uri}')
    #                 recording_rec = None
    #         else:
    #             recording_rec = None
    #         if recording_rec is None:
    #             recording_rec = _find_recording(x, study_set_name, study_name, recording_name)
    #             print(recording_rec)

    #             sorting_true_uri = recording_rec['sortingTrueUri']
    #             sorting_true_obj = kc.load_json(sorting_true_uri, channel='spikeforest')
    #             firings_uri = sorting_true_obj['firings']
    #             firings_true_local_path = kc.load_file(firings_uri, channel='spikeforest')
    #             print(f'Storing firings_true.mda for {study_name}/{recording_name}')
    #             sorting_true_obj['firings'] = kcl.store_file(firings_true_local_path) + '?firings_true.mda'
    #             sorting_true_obj['samplerate'] = recording_rec['sampleRateHz']
    #             recording_rec['sortingTrueObject'] = sorting_true_obj

    #             recording_uri = recording_rec['recordingUri']
    #             recording_obj = kc.load_json(recording_uri, channel='spikeforest')
    #             raw_uri = recording_obj['raw']
    #             raw_local_path = kc.load_file(raw_uri, channel='spikeforest')
    #             print(f'Storing raw.mda for {study_name}/{recording_name}')
    #             recording_obj['raw'] = kcl.store_file(raw_local_path) + '?raw.mda'
    #             recording_rec['recordingObject'] = recording_obj

    #             kcl.set_mutable(k, kcl.store_json(recording_rec))
    #         recording_records.append(recording_rec)
    # spikeforest_recordings_uri = kcl.store_json({'recordings': recording_records}) + '?spikeforest-recordings.json'
    # kcl.set_mutable('spikeforest-recordings', spikeforest_recordings_uri)
    # print(spikeforest_recordings_uri)

def _sha1_to_ipfs_uri(uri: str, label):
    return kcl.store_file(kc.load_file(uri, channel='spikeforest')) + f'?label={label}'

if __name__ == '__main__':
    main()