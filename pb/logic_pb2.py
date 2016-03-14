# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: logic.proto

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
  name='logic.proto',
  package='logic',
  serialized_pb=_b('\n\x0blogic.proto\x12\x05logic\"\xc0\x06\n\rPendingPolicy\x12\r\n\x05stkid\x18\x01 \x02(\t\x12\x12\n\nactiveflag\x18\x02 \x01(\x05\x12\x13\n\x0bpending_qty\x18\x03 \x01(\x05\x12\x12\n\ncancel_spd\x18\x04 \x01(\x01\x12\x11\n\tlevel_qty\x18\x05 \x01(\x05\x12\x14\n\x0cqty_perlevel\x18\x06 \x01(\x05\x12\x13\n\x0b\x61\x63\x63u_th_amt\x18\x07 \x01(\x01\x12\x11\n\tknock_amt\x18\x08 \x01(\x01\x12\x11\n\tpool_size\x18\t \x01(\x05\x12\x11\n\ttotal_num\x18\n \x01(\x05\x12\x31\n\tfut_th_li\x18\x0b \x03(\x0b\x32\x1e.logic.PendingPolicy.future_th\x12\x10\n\x08traderid\x18\x0c \x02(\t\x12\x11\n\tproductid\x18\r \x02(\t\x12\x0f\n\x07rf_flag\x18\x0e \x01(\x05\x12\x10\n\x08\x64iscount\x18\x0f \x01(\x01\x12\x0f\n\x07max_num\x18\x10 \x01(\x05\x12\x16\n\x0erf_accu_th_qty\x18\x11 \x01(\x01\x12\x0c\n\x04stop\x18\x12 \x01(\x05\x12\x0f\n\x07the_amt\x18\x13 \x01(\x01\x12\x13\n\x0bpolicy_type\x18\x14 \x02(\t\x12\x13\n\x0blevel_inter\x18\x15 \x02(\x05\x12\x1b\n\x13\x66uture_reorder_step\x18\x16 \x01(\x05\x12%\n\x17\x66uture_reorder_interval\x18\x17 \x01(\x05:\x04\x35\x30\x30\x30\x12 \n\x18\x66uture_reorder_max_times\x18\x18 \x01(\x05\x12\x13\n\x0bprice_ratio\x18\x19 \x02(\x05\x12\x16\n\x0e\x64\x65layed_single\x18\x1a \x02(\r\x12\x13\n\x0b\x64\x65layed_max\x18\x1b \x02(\r\x12 \n\x18single_fut_hedge_percent\x18\x1c \x02(\x05\x12\x18\n\x10if_hedge_percent\x18\x1d \x02(\x05\x12\x15\n\rpremium_ratio\x18\x1e \x01(\r\x12\x16\n\x0e\x64iscount_ratio\x18\x1f \x01(\r\x12\x1e\n\x16\x65tf_iopv_premium_ratio\x18  \x01(\r\x12\x1f\n\x17\x65tf_iopv_discount_ratio\x18! \x01(\r\x1a+\n\tfuture_th\x12\x0e\n\x06\x66ut_id\x18\x01 \x02(\t\x12\x0e\n\x06the_th\x18\x02 \x02(\x01\"\xbb\x03\n\rFutSwapPolicy\x12\x11\n\tpool_size\x18\x01 \x01(\x05\x12\x11\n\ttotal_num\x18\x02 \x01(\x05\x12\x0e\n\x06th_net\x18\x03 \x01(\x05\x12\x12\n\npos_spread\x18\x04 \x01(\x01\x12\x12\n\nneg_spread\x18\x05 \x01(\x01\x12\x10\n\x08\x63urr_fut\x18\x06 \x02(\t\x12\x10\n\x08next_fut\x18\x07 \x02(\t\x12\x13\n\x0b\x63urr_is_act\x18\x08 \x02(\x05\x12\x14\n\x0c\x63urr_tri_qty\x18\t \x01(\x05\x12\x14\n\x0cnext_tri_qty\x18\n \x01(\x05\x12\x10\n\x08traderid\x18\x0b \x02(\t\x12\x11\n\tproductid\x18\x0c \x02(\t\x12\x0c\n\x04stop\x18\r \x01(\x05\x12\x14\n\x0creorder_flag\x18\x0e \x02(\x05\x12\x1e\n\x10reorder_interval\x18\x0f \x01(\x05:\x04\x33\x30\x30\x30\x12\x19\n\x11reorder_max_times\x18\x10 \x01(\x05\x12\x12\n\nactive_per\x18\x11 \x02(\x05\x12\x0f\n\x07pos_per\x18\x12 \x01(\x01\x12\x0f\n\x07neg_per\x18\x13 \x01(\x01\x12\x15\n\rpremium_ratio\x18\x14 \x01(\r\x12\x16\n\x0e\x64iscount_ratio\x18\x15 \x01(\r\"@\n\nPolicyResp\x12\x10\n\x08ret_code\x18\x01 \x02(\x05\x12\x0b\n\x03key\x18\x02 \x02(\t\x12\x13\n\x0bpolicy_type\x18\x03 \x02(\t\"\xbd\x01\n\x0cPolicyStatus\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\x0e\n\x06status\x18\x02 \x02(\t\x12\x11\n\tknock_amt\x18\x03 \x01(\x01\x12\x10\n\x08\x66inished\x18\x04 \x01(\x05\x12\x0e\n\x06\x66\x61iled\x18\x05 \x01(\x05\x12\x0c\n\x04part\x18\x06 \x01(\x05\x12\x0e\n\x06\x63reate\x18\x07 \x01(\x05\x12\x12\n\nprogressed\x18\x08 \x01(\x05\x12\x13\n\x0bpolicy_type\x18\t \x02(\t\x12\x14\n\x0crf_knock_qty\x18\n \x01(\x05\"7\n\x0ePolicyPosition\x12\x10\n\x08position\x18\x01 \x02(\x01\x12\x13\n\x0bpolicy_type\x18\x02 \x02(\t\" \n\x0bQueryPolicy\x12\x11\n\ttrader_id\x18\x01 \x02(\t\"#\n\x0cPostionClear\x12\x13\n\x0bpolicy_type\x18\x01 \x02(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PENDINGPOLICY_FUTURE_TH = _descriptor.Descriptor(
  name='future_th',
  full_name='logic.PendingPolicy.future_th',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='fut_id', full_name='logic.PendingPolicy.future_th.fut_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='the_th', full_name='logic.PendingPolicy.future_th.the_th', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=812,
  serialized_end=855,
)

_PENDINGPOLICY = _descriptor.Descriptor(
  name='PendingPolicy',
  full_name='logic.PendingPolicy',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='stkid', full_name='logic.PendingPolicy.stkid', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='activeflag', full_name='logic.PendingPolicy.activeflag', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pending_qty', full_name='logic.PendingPolicy.pending_qty', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cancel_spd', full_name='logic.PendingPolicy.cancel_spd', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level_qty', full_name='logic.PendingPolicy.level_qty', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='qty_perlevel', full_name='logic.PendingPolicy.qty_perlevel', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accu_th_amt', full_name='logic.PendingPolicy.accu_th_amt', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='knock_amt', full_name='logic.PendingPolicy.knock_amt', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pool_size', full_name='logic.PendingPolicy.pool_size', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='total_num', full_name='logic.PendingPolicy.total_num', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fut_th_li', full_name='logic.PendingPolicy.fut_th_li', index=10,
      number=11, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='traderid', full_name='logic.PendingPolicy.traderid', index=11,
      number=12, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='productid', full_name='logic.PendingPolicy.productid', index=12,
      number=13, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rf_flag', full_name='logic.PendingPolicy.rf_flag', index=13,
      number=14, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='discount', full_name='logic.PendingPolicy.discount', index=14,
      number=15, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_num', full_name='logic.PendingPolicy.max_num', index=15,
      number=16, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rf_accu_th_qty', full_name='logic.PendingPolicy.rf_accu_th_qty', index=16,
      number=17, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stop', full_name='logic.PendingPolicy.stop', index=17,
      number=18, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='the_amt', full_name='logic.PendingPolicy.the_amt', index=18,
      number=19, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy_type', full_name='logic.PendingPolicy.policy_type', index=19,
      number=20, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='level_inter', full_name='logic.PendingPolicy.level_inter', index=20,
      number=21, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_reorder_step', full_name='logic.PendingPolicy.future_reorder_step', index=21,
      number=22, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_reorder_interval', full_name='logic.PendingPolicy.future_reorder_interval', index=22,
      number=23, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=5000,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='future_reorder_max_times', full_name='logic.PendingPolicy.future_reorder_max_times', index=23,
      number=24, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='price_ratio', full_name='logic.PendingPolicy.price_ratio', index=24,
      number=25, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='delayed_single', full_name='logic.PendingPolicy.delayed_single', index=25,
      number=26, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='delayed_max', full_name='logic.PendingPolicy.delayed_max', index=26,
      number=27, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='single_fut_hedge_percent', full_name='logic.PendingPolicy.single_fut_hedge_percent', index=27,
      number=28, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='if_hedge_percent', full_name='logic.PendingPolicy.if_hedge_percent', index=28,
      number=29, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='premium_ratio', full_name='logic.PendingPolicy.premium_ratio', index=29,
      number=30, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='discount_ratio', full_name='logic.PendingPolicy.discount_ratio', index=30,
      number=31, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='etf_iopv_premium_ratio', full_name='logic.PendingPolicy.etf_iopv_premium_ratio', index=31,
      number=32, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='etf_iopv_discount_ratio', full_name='logic.PendingPolicy.etf_iopv_discount_ratio', index=32,
      number=33, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_PENDINGPOLICY_FUTURE_TH, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=23,
  serialized_end=855,
)


_FUTSWAPPOLICY = _descriptor.Descriptor(
  name='FutSwapPolicy',
  full_name='logic.FutSwapPolicy',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pool_size', full_name='logic.FutSwapPolicy.pool_size', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='total_num', full_name='logic.FutSwapPolicy.total_num', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='th_net', full_name='logic.FutSwapPolicy.th_net', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pos_spread', full_name='logic.FutSwapPolicy.pos_spread', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='neg_spread', full_name='logic.FutSwapPolicy.neg_spread', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='curr_fut', full_name='logic.FutSwapPolicy.curr_fut', index=5,
      number=6, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='next_fut', full_name='logic.FutSwapPolicy.next_fut', index=6,
      number=7, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='curr_is_act', full_name='logic.FutSwapPolicy.curr_is_act', index=7,
      number=8, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='curr_tri_qty', full_name='logic.FutSwapPolicy.curr_tri_qty', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='next_tri_qty', full_name='logic.FutSwapPolicy.next_tri_qty', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='traderid', full_name='logic.FutSwapPolicy.traderid', index=10,
      number=11, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='productid', full_name='logic.FutSwapPolicy.productid', index=11,
      number=12, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stop', full_name='logic.FutSwapPolicy.stop', index=12,
      number=13, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reorder_flag', full_name='logic.FutSwapPolicy.reorder_flag', index=13,
      number=14, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reorder_interval', full_name='logic.FutSwapPolicy.reorder_interval', index=14,
      number=15, type=5, cpp_type=1, label=1,
      has_default_value=True, default_value=3000,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='reorder_max_times', full_name='logic.FutSwapPolicy.reorder_max_times', index=15,
      number=16, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='active_per', full_name='logic.FutSwapPolicy.active_per', index=16,
      number=17, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pos_per', full_name='logic.FutSwapPolicy.pos_per', index=17,
      number=18, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='neg_per', full_name='logic.FutSwapPolicy.neg_per', index=18,
      number=19, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='premium_ratio', full_name='logic.FutSwapPolicy.premium_ratio', index=19,
      number=20, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='discount_ratio', full_name='logic.FutSwapPolicy.discount_ratio', index=20,
      number=21, type=13, cpp_type=3, label=1,
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
  serialized_start=858,
  serialized_end=1301,
)


_POLICYRESP = _descriptor.Descriptor(
  name='PolicyResp',
  full_name='logic.PolicyResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ret_code', full_name='logic.PolicyResp.ret_code', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='logic.PolicyResp.key', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy_type', full_name='logic.PolicyResp.policy_type', index=2,
      number=3, type=9, cpp_type=9, label=2,
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
  serialized_start=1303,
  serialized_end=1367,
)


_POLICYSTATUS = _descriptor.Descriptor(
  name='PolicyStatus',
  full_name='logic.PolicyStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='logic.PolicyStatus.key', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='logic.PolicyStatus.status', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='knock_amt', full_name='logic.PolicyStatus.knock_amt', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='finished', full_name='logic.PolicyStatus.finished', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='failed', full_name='logic.PolicyStatus.failed', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='part', full_name='logic.PolicyStatus.part', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='create', full_name='logic.PolicyStatus.create', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='progressed', full_name='logic.PolicyStatus.progressed', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy_type', full_name='logic.PolicyStatus.policy_type', index=8,
      number=9, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rf_knock_qty', full_name='logic.PolicyStatus.rf_knock_qty', index=9,
      number=10, type=5, cpp_type=1, label=1,
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
  serialized_start=1370,
  serialized_end=1559,
)


_POLICYPOSITION = _descriptor.Descriptor(
  name='PolicyPosition',
  full_name='logic.PolicyPosition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='position', full_name='logic.PolicyPosition.position', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='policy_type', full_name='logic.PolicyPosition.policy_type', index=1,
      number=2, type=9, cpp_type=9, label=2,
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
  serialized_start=1561,
  serialized_end=1616,
)


_QUERYPOLICY = _descriptor.Descriptor(
  name='QueryPolicy',
  full_name='logic.QueryPolicy',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='trader_id', full_name='logic.QueryPolicy.trader_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
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
  serialized_start=1618,
  serialized_end=1650,
)


_POSTIONCLEAR = _descriptor.Descriptor(
  name='PostionClear',
  full_name='logic.PostionClear',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='policy_type', full_name='logic.PostionClear.policy_type', index=0,
      number=1, type=9, cpp_type=9, label=2,
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
  serialized_start=1652,
  serialized_end=1687,
)

_PENDINGPOLICY_FUTURE_TH.containing_type = _PENDINGPOLICY
_PENDINGPOLICY.fields_by_name['fut_th_li'].message_type = _PENDINGPOLICY_FUTURE_TH
DESCRIPTOR.message_types_by_name['PendingPolicy'] = _PENDINGPOLICY
DESCRIPTOR.message_types_by_name['FutSwapPolicy'] = _FUTSWAPPOLICY
DESCRIPTOR.message_types_by_name['PolicyResp'] = _POLICYRESP
DESCRIPTOR.message_types_by_name['PolicyStatus'] = _POLICYSTATUS
DESCRIPTOR.message_types_by_name['PolicyPosition'] = _POLICYPOSITION
DESCRIPTOR.message_types_by_name['QueryPolicy'] = _QUERYPOLICY
DESCRIPTOR.message_types_by_name['PostionClear'] = _POSTIONCLEAR

PendingPolicy = _reflection.GeneratedProtocolMessageType('PendingPolicy', (_message.Message,), dict(

  future_th = _reflection.GeneratedProtocolMessageType('future_th', (_message.Message,), dict(
    DESCRIPTOR = _PENDINGPOLICY_FUTURE_TH,
    __module__ = 'logic_pb2'
    # @@protoc_insertion_point(class_scope:logic.PendingPolicy.future_th)
    ))
  ,
  DESCRIPTOR = _PENDINGPOLICY,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.PendingPolicy)
  ))
_sym_db.RegisterMessage(PendingPolicy)
_sym_db.RegisterMessage(PendingPolicy.future_th)

FutSwapPolicy = _reflection.GeneratedProtocolMessageType('FutSwapPolicy', (_message.Message,), dict(
  DESCRIPTOR = _FUTSWAPPOLICY,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.FutSwapPolicy)
  ))
_sym_db.RegisterMessage(FutSwapPolicy)

PolicyResp = _reflection.GeneratedProtocolMessageType('PolicyResp', (_message.Message,), dict(
  DESCRIPTOR = _POLICYRESP,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.PolicyResp)
  ))
_sym_db.RegisterMessage(PolicyResp)

PolicyStatus = _reflection.GeneratedProtocolMessageType('PolicyStatus', (_message.Message,), dict(
  DESCRIPTOR = _POLICYSTATUS,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.PolicyStatus)
  ))
_sym_db.RegisterMessage(PolicyStatus)

PolicyPosition = _reflection.GeneratedProtocolMessageType('PolicyPosition', (_message.Message,), dict(
  DESCRIPTOR = _POLICYPOSITION,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.PolicyPosition)
  ))
_sym_db.RegisterMessage(PolicyPosition)

QueryPolicy = _reflection.GeneratedProtocolMessageType('QueryPolicy', (_message.Message,), dict(
  DESCRIPTOR = _QUERYPOLICY,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.QueryPolicy)
  ))
_sym_db.RegisterMessage(QueryPolicy)

PostionClear = _reflection.GeneratedProtocolMessageType('PostionClear', (_message.Message,), dict(
  DESCRIPTOR = _POSTIONCLEAR,
  __module__ = 'logic_pb2'
  # @@protoc_insertion_point(class_scope:logic.PostionClear)
  ))
_sym_db.RegisterMessage(PostionClear)


# @@protoc_insertion_point(module_scope)
