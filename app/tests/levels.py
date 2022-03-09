from dataclasses import dataclass
from typing import List, Dict

FIRST_LEVELS_CONT_REGS = [16, 17292, 33280, 0, 0, 23048, 0, 0, 0, 0, 0, 0, 0, 0, 2, 512]


@dataclass
class Level:
    name: str
    first_cont_output: bytes
    win_output: bytes
    lose_output: bytes
    solution_hex: str
    first_cont_regs: List[int]
    first_cont_mem_update: Dict[int, bytes]


new_orleans = Level(name='New Orleans',
                    first_cont_output=b'Enter the password to continue\n',
                    win_output=b'Access Granted!\n\n',  # TODO: why two \n?
                    lose_output=b'Invalid password; try again.\n',
                    solution_hex='40462d77717056',
                    first_cont_regs=FIRST_LEVELS_CONT_REGS,
                    first_cont_mem_update={336: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08Z\x00\x00',
                                           9216: b'@F-wqpV\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                                           17296: b'\x8eE\x02\x00\x9cCd\x00\xbaDND\x00\x00\x00\x00',
                                           17280: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00DE\x00\x00'})
# TODO: this only happens in the original ,16: b'0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'})

sydney = Level(name='Sydney',
               first_cont_output=b'Enter the password to continue.\n',
               win_output=b'Access Granted!\n\n',  # TODO: why two \n?
               lose_output=b'Invalid password; try again.\n',
               solution_hex='5477403339363626',
               first_cont_regs=FIRST_LEVELS_CONT_REGS,
               first_cont_mem_update={17296: b'`E\x02\x00\x9cCd\x00\x88DJD\x00\x00\x00\x00',
                                      17280: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16E\x00\x00'})
# TODO: this only happens in the original ,16: b'0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'})

reykjavik = Level(name='Reykjavik',
                  first_cont_output=b'what\'s the password?\n',
                  win_output=b'\n',
                  lose_output=b'',
                  solution_hex='c2d3',
                  first_cont_regs=[16, 17358, 33280, 0, 17406, 23048, 0, 0, 0, 0, 0, 17716, 248, 196, 2, 512],
                  first_cont_mem_update={9216: b'\x0b\x12\x04\x12\x04A$R1P\xe0\xff;@ E',
                                         9408: b'\xda\xa7\xdb?\x8d<M\x18G6\xdf\xa6E\x9a$a',
                                         9520: b'_\xf2=\xc7YS\x88&\xd0\xb5\xd9\xf8c\x9e\xe9p',
                                         9504: b'O\x03\x8e\xc9\x93\x95J\x15\xce;\xfd\x1ewy\xc9\xc3',
                                         9232: b'\x07<\x1bS\x8f\x11\x0f\x12\x03\x12\xb0\x12d$!R',
                                         9264: b'!R0\x12\x1f\x00?@\xdc\xff\x0fT\x0f\x12#\x12',
                                         9552: b'\xd6\x82\x1b\xe5\xab s\x89H\xaa\x1f\xa3G/\xa5d',
                                         # TODO: should be 16: b'0A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                                         336: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08Z\x00\x00',
                                         9344: b'"\xdcE\xb9By-U\x85\x8e\xa4\xa2g\xd7\x14\xae',
                                         9584: b"\xd5\xf4\xa8Q\xc2C'}\xa4\xca\x1ek\x00\x00\x00\x00",
                                         9328: b'2\xd0\x00\x80\xb0\x12\x10\x002A0A\xd2\x1a\x18\x9a',
                                         9536: b'\x01\xcd!\x19\xcaj\xd1,\x97\xe2u8\x96\xc5\x8f(',
                                         9472: b'<V\x13\xaf\xe5{\x8a\xbf0@\xc57en\x82x',
                                         9392: b'\xfa\x9bftN!*k\xb1C\x91Q=\xcc\xa6\xf5',
                                         17344: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00x$',
                                         9376: b'\xd27\xa2S"\xe4f\xaf\xc1\xa5\x93\x8b\x89q\x9b\x88',
                                         9280: b'\xb0\x12d$1P\x06\x00\xb4\x90\xc2\xd3\xdc\xff\x05 ',
                                         9360: b'\xa1\x19v\xf6B\xcb\x1c\x04\x0e\xfa\xa6\x1bt\xa7Ak',
                                         9440: b'c\x10:\xb3a+\x0b\xd9H?N\x04XpL8',
                                         9456: b'\xc9<\xff6\x0e\x01\x7f>\xfaU\xae\xef\x05\x1c$,',
                                         17360: b'\x01\x00D$\x02\x00\xdaC\x1f\x00\x00\x00\x00\x00\x00\x00',
                                         9568: b'\xde-\xb7\x10\x90\x81R\x05\x8dD\xcf\xf4\xbc.Wz',
                                         9312: b';A0A\x1eA\x02\x00\x02\x12\x0fN\x8f\x10\x02O',
                                         9424: b'\x92\x1d2\x91\x14\xe6\x81W\xb0\xfe-\xdd@\x0b\x86\x88',
                                         9488: b'\x9a\xf9\x9d\x02\xbe\x83\xb3\x8c\xe1\x81:\xd89Z\xfc\xe3',
                                         9248: b'oKO\x93\xf6#0\x12\n\x00\x03\x12\xb0\x12d$',
                                         9296: b'0\x12\x7f\x00\xb0\x12d$!S1P \x004A',
                                         17392: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ND'})

levels = [new_orleans, sydney, reykjavik]
