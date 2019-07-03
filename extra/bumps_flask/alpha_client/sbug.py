import websocket
if __name__ == "__main__":
    msg = {"header": "bumps client", "tag": "sbag", "message_time": {"year": 2019, "month": 7, "date": 2, "hour": 9, "minutes": 5, "seconds": 30, "milliseconds": 281}, "command": "StartFit", "fit_problem": "import bumps\nfrom bumps.names import *\n\ndef line (x, m, b=0):\n    return (m*x + b)\n\nx = [1,2,3,4,5,6]\ny = [2.1,4.1,6.3,8.03,9.6,11.9]\nx = [1,2,3,4,5,6]\ny = [2,4,6,8,10,12]\ndy = [0.05,0.05,0.2,0.05,0.2,0.2]\ndy = [0.2,0.2,0.2,0.2,0.2,0.2]\n\nM = Curve(line,x,y,dy,m=2,b=2)\n\nM.m.range(0,4)\nM.b.range(-5,5)\n\nproblem = FitProblem(M)", "problem_file": "", "params": {"algorithm": "newton", "steps": "100", "burns": "100"}, "multi_processing": "none", "row_id": "cbox3"}
    smsg=str(msg)
    ws = websocket.create_connection("ws://bumps_gui:4567")
    ws.send(smsg)
    print(f'{ws.recv()}')
    ws.close()