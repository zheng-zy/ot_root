# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: risk_server_future.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='risk_server_future.proto',
  package='risk_server_future',
  serialized_pb=_b('\n\x18risk_server_future.proto\x12\x12risk_server_future\"\xd6\x0b\n\x15\x66uture_order_set_info\x12%\n\x1d\x61ll_future_order_count_second\x18\x01 \x02(\r\x12#\n\x1b\x61ll_future_order_count_most\x18\x02 \x02(\r\x12%\n\x1dIF_future_single_order_second\x18\x03 \x02(\r\x12#\n\x1bIF_future_single_order_most\x18\x04 \x02(\r\x12%\n\x1dIC_future_single_order_second\x18\x05 \x02(\r\x12#\n\x1bIC_future_single_order_most\x18\x06 \x02(\r\x12%\n\x1dIH_future_single_order_second\x18\x07 \x02(\r\x12#\n\x1bIH_future_single_order_most\x18\x08 \x02(\r\x12!\n\x19\x66uture_order_count_second\x18\t \x02(\r\x12\x1f\n\x17\x66uture_order_count_most\x18\n \x02(\r\x12&\n\x1e\x61ll_future_order_volume_second\x18\x0b \x02(\r\x12$\n\x1c\x61ll_future_order_volume_most\x18\x0c \x02(\r\x12%\n\x1dIF_future_order_volume_second\x18\r \x02(\r\x12#\n\x1bIF_future_order_volume_most\x18\x0e \x02(\r\x12%\n\x1dIC_future_order_volume_second\x18\x0f \x02(\r\x12#\n\x1bIC_future_order_volume_most\x18\x10 \x02(\r\x12%\n\x1dIH_future_order_volume_second\x18\x11 \x02(\r\x12#\n\x1bIH_future_order_volume_most\x18\x12 \x02(\r\x12)\n!account_future_order_count_second\x18\x13 \x02(\r\x12\'\n\x1f\x61\x63\x63ount_future_order_count_most\x18\x14 \x02(\r\x12\'\n\x1f\x61\x63\x63ount_future_buy_order_second\x18\x15 \x02(\r\x12%\n\x1d\x61\x63\x63ount_future_buy_order_most\x18\x16 \x02(\t\x12(\n account_future_sell_order_second\x18\x17 \x02(\r\x12&\n\x1e\x61\x63\x63ount_future_sell_order_most\x18\x18 \x02(\t\x12.\n&account_all_future_order_volume_second\x18\x19 \x02(\r\x12,\n$account_all_future_order_volume_most\x18\x1a \x02(\r\x12-\n%account_IF_future_order_volume_second\x18\x1b \x02(\r\x12+\n#account_IF_future_order_volume_most\x18\x1c \x02(\r\x12-\n%account_IC_future_order_volume_second\x18\x1d \x02(\r\x12+\n#account_IC_future_order_volume_most\x18\x1e \x02(\r\x12-\n%account_IH_future_order_volume_second\x18\x1f \x02(\r\x12+\n#account_IH_future_order_volume_most\x18  \x02(\r\x12\x39\n1account_IF_future_open_position_order_volume_most\x18! \x02(\r\x12\x39\n1account_IC_future_open_position_order_volume_most\x18\" \x02(\r\x12\x39\n1account_IH_future_open_position_order_volume_most\x18# \x02(\r\"W\n\x14\x46uture_Order_Set_Req\x12?\n\x0c\x66uture_order\x18\x02 \x02(\x0b\x32).risk_server_future.future_order_set_info\"6\n\x15\x46uture_Order_Set_Resp\x12\x10\n\x08ret_code\x18\x01 \x02(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\"y\n\x17\x46uture_Order_Query_Info\x12\x10\n\x08ret_code\x18\x01 \x02(\x05\x12?\n\x0c\x66uture_order\x18\x02 \x01(\x0b\x32).risk_server_future.future_order_set_info\x12\x0b\n\x03msg\x18\x03 \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_FUTURE_ORDER_SET_INFO = _descriptor.Descriptor(
  name='future_order_set_info',
  full_name='risk_server_future.future_order_set_info',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='all_future_order_count_second', full_name='risk_server_future.future_order_set_info.all_future_order_count_second', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='all_future_order_count_most', full_name='risk_server_future.future_order_set_info.all_future_order_count_most', index=1,
      number=2, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IF_future_single_order_second', full_name='risk_server_future.future_order_set_info.IF_future_single_order_second', index=2,
      number=3, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IF_future_single_order_most', full_name='risk_server_future.future_order_set_info.IF_future_single_order_most', index=3,
      number=4, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IC_future_single_order_second', full_name='risk_server_future.future_order_set_info.IC_future_single_order_second', index=4,
      number=5, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IC_future_single_order_most', full_name='risk_server_future.future_order_set_info.IC_future_single_order_most', index=5,
      number=6, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IH_future_single_order_second', full_name='risk_server_future.future_order_set_info.IH_future_single_order_second', index=6,
      number=7, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IH_future_single_order_most', full_name='risk_server_future.future_order_set_info.IH_future_single_order_most', index=7,
      number=8, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_order_count_second', full_name='risk_server_future.future_order_set_info.future_order_count_second', index=8,
      number=9, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_order_count_most', full_name='risk_server_future.future_order_set_info.future_order_count_most', index=9,
      number=10, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='all_future_order_volume_second', full_name='risk_server_future.future_order_set_info.all_future_order_volume_second', index=10,
      number=11, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='all_future_order_volume_most', full_name='risk_server_future.future_order_set_info.all_future_order_volume_most', index=11,
      number=12, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IF_future_order_volume_second', full_name='risk_server_future.future_order_set_info.IF_future_order_volume_second', index=12,
      number=13, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IF_future_order_volume_most', full_name='risk_server_future.future_order_set_info.IF_future_order_volume_most', index=13,
      number=14, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IC_future_order_volume_second', full_name='risk_server_future.future_order_set_info.IC_future_order_volume_second', index=14,
      number=15, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IC_future_order_volume_most', full_name='risk_server_future.future_order_set_info.IC_future_order_volume_most', index=15,
      number=16, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IH_future_order_volume_second', full_name='risk_server_future.future_order_set_info.IH_future_order_volume_second', index=16,
      number=17, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='IH_future_order_volume_most', full_name='risk_server_future.future_order_set_info.IH_future_order_volume_most', index=17,
      number=18, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_order_count_second', full_name='risk_server_future.future_order_set_info.account_future_order_count_second', index=18,
      number=19, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_order_count_most', full_name='risk_server_future.future_order_set_info.account_future_order_count_most', index=19,
      number=20, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_buy_order_second', full_name='risk_server_future.future_order_set_info.account_future_buy_order_second', index=20,
      number=21, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_buy_order_most', full_name='risk_server_future.future_order_set_info.account_future_buy_order_most', index=21,
      number=22, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_sell_order_second', full_name='risk_server_future.future_order_set_info.account_future_sell_order_second', index=22,
      number=23, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_future_sell_order_most', full_name='risk_server_future.future_order_set_info.account_future_sell_order_most', index=23,
      number=24, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_all_future_order_volume_second', full_name='risk_server_future.future_order_set_info.account_all_future_order_volume_second', index=24,
      number=25, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_all_future_order_volume_most', full_name='risk_server_future.future_order_set_info.account_all_future_order_volume_most', index=25,
      number=26, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IF_future_order_volume_second', full_name='risk_server_future.future_order_set_info.account_IF_future_order_volume_second', index=26,
      number=27, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IF_future_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IF_future_order_volume_most', index=27,
      number=28, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IC_future_order_volume_second', full_name='risk_server_future.future_order_set_info.account_IC_future_order_volume_second', index=28,
      number=29, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IC_future_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IC_future_order_volume_most', index=29,
      number=30, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IH_future_order_volume_second', full_name='risk_server_future.future_order_set_info.account_IH_future_order_volume_second', index=30,
      number=31, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IH_future_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IH_future_order_volume_most', index=31,
      number=32, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IF_future_open_position_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IF_future_open_position_order_volume_most', index=32,
      number=33, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IC_future_open_position_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IC_future_open_position_order_volume_most', index=33,
      number=34, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_IH_future_open_position_order_volume_most', full_name='risk_server_future.future_order_set_info.account_IH_future_open_position_order_volume_most', index=34,
      number=35, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=49,
  serialized_end=1543,
)


_FUTURE_ORDER_SET_REQ = _descriptor.Descriptor(
  name='Future_Order_Set_Req',
  full_name='risk_server_future.Future_Order_Set_Req',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='future_order', full_name='risk_server_future.Future_Order_Set_Req.future_order', index=0,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1545,
  serialized_end=1632,
)


_FUTURE_ORDER_SET_RESP = _descriptor.Descriptor(
  name='Future_Order_Set_Resp',
  full_name='risk_server_future.Future_Order_Set_Resp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret_code', full_name='risk_server_future.Future_Order_Set_Resp.ret_code', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg', full_name='risk_server_future.Future_Order_Set_Resp.msg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1634,
  serialized_end=1688,
)


_FUTURE_ORDER_QUERY_INFO = _descriptor.Descriptor(
  name='Future_Order_Query_Info',
  full_name='risk_server_future.Future_Order_Query_Info',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret_code', full_name='risk_server_future.Future_Order_Query_Info.ret_code', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_order', full_name='risk_server_future.Future_Order_Query_Info.future_order', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg', full_name='risk_server_future.Future_Order_Query_Info.msg', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1690,
  serialized_end=1811,
)

_FUTURE_ORDER_SET_REQ.fields_by_name['future_order'].message_type = _FUTURE_ORDER_SET_INFO
_FUTURE_ORDER_QUERY_INFO.fields_by_name['future_order'].message_type = _FUTURE_ORDER_SET_INFO
DESCRIPTOR.message_types_by_name['future_order_set_info'] = _FUTURE_ORDER_SET_INFO
DESCRIPTOR.message_types_by_name['Future_Order_Set_Req'] = _FUTURE_ORDER_SET_REQ
DESCRIPTOR.message_types_by_name['Future_Order_Set_Resp'] = _FUTURE_ORDER_SET_RESP
DESCRIPTOR.message_types_by_name['Future_Order_Query_Info'] = _FUTURE_ORDER_QUERY_INFO

future_order_set_info = _reflection.GeneratedProtocolMessageType('future_order_set_info', (_message.Message,), dict(
  DESCRIPTOR = _FUTURE_ORDER_SET_INFO,
  __module__ = 'risk_server_future_pb2'
  # @@protoc_insertion_point(class_scope:risk_server_future.future_order_set_info)
  ))
_sym_db.RegisterMessage(future_order_set_info)

Future_Order_Set_Req = _reflection.GeneratedProtocolMessageType('Future_Order_Set_Req', (_message.Message,), dict(
  DESCRIPTOR = _FUTURE_ORDER_SET_REQ,
  __module__ = 'risk_server_future_pb2'
  # @@protoc_insertion_point(class_scope:risk_server_future.Future_Order_Set_Req)
  ))
_sym_db.RegisterMessage(Future_Order_Set_Req)

Future_Order_Set_Resp = _reflection.GeneratedProtocolMessageType('Future_Order_Set_Resp', (_message.Message,), dict(
  DESCRIPTOR = _FUTURE_ORDER_SET_RESP,
  __module__ = 'risk_server_future_pb2'
  # @@protoc_insertion_point(class_scope:risk_server_future.Future_Order_Set_Resp)
  ))
_sym_db.RegisterMessage(Future_Order_Set_Resp)

Future_Order_Query_Info = _reflection.GeneratedProtocolMessageType('Future_Order_Query_Info', (_message.Message,), dict(
  DESCRIPTOR = _FUTURE_ORDER_QUERY_INFO,
  __module__ = 'risk_server_future_pb2'
  # @@protoc_insertion_point(class_scope:risk_server_future.Future_Order_Query_Info)
  ))
_sym_db.RegisterMessage(Future_Order_Query_Info)


# @@protoc_insertion_point(module_scope)
