import pcbnew

#/Users/dreigada/Documents/KiCad/6.0/scripting/plugins/positiondiodes.py
#filename = "/Users/dreigada/myworkspace/slimy-keyboard/pcb/position_diodes.py"
#exec(compile(open(filename, "rb").read(), filename, "exec"))

def get_layer_by_name(name):
    i = pcbnew.PCBNEW_LAYER_ID_START

    for i in range(i, pcbnew.PCBNEW_LAYER_ID_START + pcbnew.PCB_LAYER_ID_COUNT):
        if pcbnew.BOARD_GetStandardLayerName(i) == name:
            return i


def place_switch(switch, i):
    i = i-1
    col = int(i % cols)
    row = int(i / cols)
    
    switch.SetPosition(pcbnew.wxPointMils(750 * col, 750 * row))
    switch.SetOrientationDegrees(0)

def move_diode(switch, diode):
    switch_position = switch.GetPosition()

    new_diode_position = switch_position + pcbnew.wxPointMils(0, -340)

    diode.SetPosition(new_diode_position)
    diode.SetOrientationDegrees(180)

def add_track(start_position, end_position, layer):
    track = pcbnew.PCB_TRACK(board)
    track.SetLayer(layer)

    track.SetStart(start_position)
    track.SetEnd(end_position)
    board.Add(track)

def trace_track(start_position, trace, layer):
    for t in trace:
        end_position = start_position + t
        add_track(start_position, end_position, layer)
        start_position = end_position

def connect_to_diode(switch):
    switch_position = switch.GetPosition()
    
    start_position = switch_position + pcbnew.wxPointMils(-350, -130)

    trace_track(start_position, [
        pcbnew.wxPointMils(0, -140),
        pcbnew.wxPointMils(70, -70),
        pcbnew.wxPointMils(125, 0)
    ], F_CU)

def connect_to_row(switch):
    switch_position = switch.GetPosition()
    
    start_position = switch_position + pcbnew.wxPointMils(150, -340)
    trace_track(start_position, [
        pcbnew.wxPointMils(70, -70),
        pcbnew.wxPointMils(660, 0),
        pcbnew.wxPointMils(20, 20),
        pcbnew.wxPointMils(0, 55),
    ], B_CU)

def connect_to_col(switch):
    switch_position = switch.GetPosition()
    
    start_position = switch_position + pcbnew.wxPointMils(300, -170)
    trace_track(start_position, [pcbnew.wxPointMils(0, 690)], F_CU)


B_CU = get_layer_by_name("B.Cu")
F_CU = get_layer_by_name("F.Cu")
board = pcbnew.GetBoard()
max_index = 54
rows = 5
cols = 12

for i in range(1, max_index + 1):
    switch = board.FindFootprintByReference("K" + str(i))
    diode = board.FindFootprintByReference("D" + str(i))
    

    place_switch(switch, i)
    move_diode(switch, diode)
    connect_to_diode(switch)

    # don't connect last column
    # if i % cols != 0:
    connect_to_row(switch)
    
    # don't connect last row
    # if i % rows != 0:
    connect_to_col(switch)

pcbnew.Refresh()