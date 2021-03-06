import pandas as pd

from notetagger import constants


def _get_text_snippet(full_note_text,
                      word_tags=constants.TAGS,
                      text_window_before=300,
                      text_window_after=300):
    for word_tag in word_tags:
        word_tag_index = full_note_text.lower().find(word_tag.replace('_', ' '))
        if word_tag_index >= 0:
            text_snippet = full_note_text[max(0, word_tag_index - text_window_before):
                                          min(len(full_note_text),
                                              word_tag_index + text_window_after)]
            text_snippet = text_snippet.replace(word_tag, '**{}**'.format(word_tag))
            return text_snippet


def create_note_set(
        predictions_path,
        notes_path,
        output_path,
        notes_to_sample=500,
        threshold=0.8):
    predictions_data = pd.read_json(predictions_path, orient='records', lines=True)
    notes_data = pd.read_json(notes_path, orient='records', lines=True)

    predictions_data['y_pred_round'] = predictions_data['y_pred'] > threshold
    df = predictions_data[predictions_data['y_pred_round'] == 1].merge(notes_data,
                                                                       on=['subject_num', 'note_id'],
                                                                       how='left')
    df = df[['note_id', 'subject_num', 'note_text']]

    # remove commas for csv saving
    df['note_text'] = df['note_text'].map(lambda x: x.replace(',', ''))
    print(df.shape)

    df['financial_snippet'] = df['note_text'].map(_get_text_snippet)
    df = df.sample(n=notes_to_sample, random_state=42)
    print(df.shape)
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    """
    Command line handler for `convert_data` function
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--predictions_path',
                        '-p',
                        default='random_forest2018-11-21v22-11_predictions.jsonl',
                        type=str,
                        help='Path to data file with model predictions')

    parser.add_argument('--notes_path',
                        '-n',
                        default='PCP_Depression_Notes_FINAL_20171104.jsonl',
                        type=str,
                        help='Path to data file with note text')

    parser.add_argument('--output_path',
                        '-o',
                        default='financial_notes_snippets.csv',
                        type=str,
                        help='Path to output file')

    parser.add_argument('--notes_to_sample',
                        '-s',
                        default=500,
                        type=int,
                        help='Number of notes to randomly sample')

    args = parser.parse_args()
    create_note_set(predictions_path=args.predictions_path,
                    notes_path=args.notes_path,
                    output_path=args.output_path,
                    notes_to_sample=args.notes_to_sample)
