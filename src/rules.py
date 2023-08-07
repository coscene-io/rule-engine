from ruleengine.engine import Rule
from ruleengine.dsl.base_conditions import msg
from ruleengine.dsl.actions import create_moment

rules = [
    Rule(msg >> "card_detection.cpp" & msg >> "detector_interface_ptr_ == nullptr",
         create_moment("算法初始化异常", "算法配置参数异常")),
    Rule(msg >> "card_detection.cpp" & msg >> "detect pose empty!",
         create_moment("没有检测到目标对接物体", "")),
    Rule(msg >> "card_detection.cpp" & msg >> "delta time is wrong! cannot get real time pose!",
         create_moment("没有获取到实时的tf数据", "相机时间戳赋值异常")),
    Rule(msg >> "pallet_deeplearning_detector.cpp" & msg >> "Error, no detected any bboxs.",
         create_moment("深度学习模块未给出结果返回", "相机成像异常，或算法泛化能力异常")),
]
