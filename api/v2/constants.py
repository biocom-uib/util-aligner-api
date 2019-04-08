String = 'stringdb'
IsoBase = 'isobase'
StringDBVirus = 'stringdbvirus'

PROCESS_TASK = 'process_alignment'
COMPARE_TASK = 'compare_alignments'
PROCESS_QUEUE = 'server_aligner'
COMPARE_QUEUE = 'server_comparer'

QUEUE_DISPATCHER = {
    PROCESS_TASK: PROCESS_QUEUE,
    COMPARE_TASK: COMPARE_QUEUE,
}
