from pcbnew import *
import pcbnew

#/Users/dreigada/Documents/KiCad/6.0/scripting/plugins/positiondiodes.py
#filename = "/Users/dreigada/myworkspace/slimy-keyboard/pcb/position_diodes.py"
#exec(compile(open(filename, "rb").read(), filename, "exec"))

def get_layer_by_name(name):
    i = pcbnew.PCBNEW_LAYER_ID_START

    for i in range(i, pcbnew.PCBNEW_LAYER_ID_START + pcbnew.PCB_LAYER_ID_COUNT):
        if pcbnew.BOARD_GetStandardLayerName(i) == name:
            return i

def calc_col(i):
    return int((i - 1) / rows)
def calc_row(i):
    return int((i - 1) % rows)
def is_right_side(i):
    return (i-1) < max_index / 2
def calc_switch_x_position(i):
    offset = 0 if is_right_side(i) else 750 * 2
    return 750 * calc_col(i) + offset
# def set_position_with_offset(component, wxPoint):
#     component.SetPosition(wxPoint + wxPointMils(4000, 4000))

def place_switch(switch, i):
    switch.SetPosition(wxPointMils(calc_switch_x_position(i), 750 * calc_row(i)))
    switch.SetOrientationDegrees(0)

def circle_diode_x_position(i):
    col = calc_col(i)
    row = calc_row(i)
    if col % 2 == 0 and row in [0, 3]:
        return 2
    elif col % 2 == 0:
        return 1
    elif row in [0, 3]:
        return 1
    else:
        return 2

# \/\/\/
def v_diode_x_position(i):
    if calc_col(i) % 2 == 0:
        # \
        return calc_row(-((i-rows)%rows -1)) 
    else:
        # /
        return calc_row(i) 

# /
def slash_diode_x_position(i):
    return calc_row(i)

# / \
def slash_half_diode_x_position(i):
    if calc_col(i) > 5:
        # \
        return calc_row(-((i-rows)%rows -1)) 
    else:
        # /
        return calc_row(i) 

    return calc_row(i)

def place_diode(diode, i):
    x_spacing = 120
    x_offset = - x_spacing * 1.5

    position = slash_half_diode_x_position(i)
    x = calc_switch_x_position(i) + position * x_spacing + x_offset
    
    diode_thickness = 102
    # 750 split for the 4 diodes (distances above and below included)
    # y = -750/2 - 150 * (calc_row(i) + 1)
    space_between = (750-(4*diode_thickness))/ 5
    y = -750/2 - (space_between + diode_thickness) * calc_row(i) - diode_thickness/2 - space_between

    diode.SetPosition(wxPointMils(x, y))
    if is_right_side(i):
        diode.SetOrientationDegrees(180)

def place_trackball():
    trackball = board.FindFootprintByReference("U3")

    # based on K24 position
    x = calc_switch_x_position(24) + 1.5 * 750
    y = 750 * calc_row(24) + (750/2 - 315)
    trackball.SetPosition(wxPointMils(x, y))

def place_display():
    display = board.FindFootprintByReference("U2")
    trackball = board.FindFootprintByReference("U3")

    # based on K24 position
    x = calc_switch_x_position(24) + 1.5 * 750
    # based on the trackball
    y = ToMils(trackball.GetPosition().y) - 1286.6
    
    display.SetPosition(wxPointMils(x, y))
#1491-

def place_mcu():
    mcu = board.FindFootprintByReference("U1")

    # based on K24 position
    x = calc_switch_x_position(24) + 1.5 * 750
    mcu.SetPosition(wxPointMils(x, -425))
    mcu.SetOrientationDegrees(-90)

def add_track(start_position, end_position, layer, net):
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net)

    track.SetLayer(layer)
    track.SetWidth(FromMils(0.005 * 1000))
    track.SetStart(start_position)
    track.SetEnd(end_position)

    board.Add(track)
    print(track.GetNet().GetNetClassName())

def trace_track(start_position, trace, layer, net):
    for t in trace:
        end_position = start_position + t
        add_track(start_position, end_position, layer, net)
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

def connect_to_col(switch, net):
    switch_position = switch.GetPosition()
    
    start_position = switch_position + pcbnew.wxPointMils(300, -170)
    trace_track(start_position, [pcbnew.wxPointMils(0, 690)], B_CU, net)


B_CU = get_layer_by_name("B.Cu")
F_CU = get_layer_by_name("F.Cu")
board = pcbnew.GetBoard()
max_index = 48
rows = 4
cols = 12



def main():
    place_trackball()
    place_display()
    place_mcu()

    for i in range(1, max_index + 1):
        switch = board.FindFootprintByReference("K" + str(i))
        diode = board.FindFootprintByReference("D" + str(i))
        
        place_switch(switch, i)
        place_diode(diode, i)
        # connect_to_diode(switch)

        # don't connect last column
        # if i % cols != 0:
        # connect_to_row(switch)
        
        # don't connect last row
        # if i % rows != 0:
        # net = (i - 1) % cols + 1
        # net = board.FindNet(f"Col{net}")
        # connect_to_col(switch, net)
    
    pcbnew.Refresh()

main()