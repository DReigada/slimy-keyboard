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
        return calc_row(-((i-rows)%rows -1)) -1
    else:
        # /
        return calc_row(i) + 1

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

def trace_track(start_position, trace, layer, net):
    for t in trace:
        end_position = start_position + t
        add_track(start_position, end_position, layer, net)
        start_position = end_position

def connect_to_diode(switch, i):
    switch_position = switch.GetPosition()

    start_position = switch_position + pcbnew.wxPointMils(300, -230)

    left = {
        0:
            [pcbnew.wxPointMils(-145, -145),
            pcbnew.wxPointMils(-158, 0),
            pcbnew.wxPointMils(-120, -120)],
        1:
            [pcbnew.wxPointMils(52, -52),
            pcbnew.wxPointMils(0, -778),
            pcbnew.wxPointMils(-355, -355)],
        2:
            [pcbnew.wxPointMils(63, -63),
            pcbnew.wxPointMils(0, -1800),
            pcbnew.wxPointMils(-245, -245)],
        3:
            [pcbnew.wxPointMils(74, -74),
            pcbnew.wxPointMils(0, -2820),
            pcbnew.wxPointMils(-134, -134)],
    }

    right = {
        0:
            [pcbnew.wxPointMils(0, -178),
            pcbnew.wxPointMils(-86, -86)],
        1:
            [pcbnew.wxPointMils(24, -24),
            pcbnew.wxPointMils(0, -937),
            pcbnew.wxPointMils(-225, -225)],
        2:
            [pcbnew.wxPointMils(35, -35),
            pcbnew.wxPointMils(0, -1717),
            pcbnew.wxPointMils(-356, -356)],
        3:
            [pcbnew.wxPointMils(46, -46),
            pcbnew.wxPointMils(0, -2500),
            pcbnew.wxPointMils(-485, -485)],
    }

    paths = left if calc_col(i) < 6 else right
    net = board.FindNet(f"Net-(D{i}-Pad2")
    trace_track(start_position, paths.get(calc_row(i), []), F_CU, net)

def connect_diode_to_row(diode, i):
    diode_position = diode.GetPosition()
    pin_position = pcbnew.wxPointMils(154, 0)

    left_trace = [
        pcbnew.wxPointMils(42, -42),
        pcbnew.wxPointMils(665, 0),
        pcbnew.wxPointMils(43, 43)]

    right_trace = [
        pcbnew.wxPointMils(-42, -42),
        pcbnew.wxPointMils(-665, 0),
        pcbnew.wxPointMils(-43, 43)]

    net = board.FindNet(f"Row{calc_row(i) + 1}")

    if calc_col(i) < 5:
        start_position = diode_position + pin_position
        trace_track(start_position, left_trace, B_CU, net)
    elif calc_col(i) > 6:
        start_position = diode_position - pin_position
        trace_track(start_position, right_trace, B_CU, net)


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
    
    start_position = switch_position + pcbnew.wxPointMils(-350, -70)
    trace_track(start_position, [pcbnew.wxPointMils(0, 690)], F_CU, net)


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
        connect_to_diode(switch, i)
        connect_diode_to_row(diode, i)

        # don't connect last column
        # if i % cols != 0:
        # connect_to_row(switch)
        
        # don't connect last row
        if calc_row(i) < 3:
            net = (i - 1) % cols + 1
            net = board.FindNet(f"Col{net}")
            connect_to_col(switch, net)
    
    pcbnew.Refresh()

main()