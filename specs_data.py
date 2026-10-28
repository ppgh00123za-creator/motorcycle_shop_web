"""
specs_data.py
ข้อมูลรายละเอียดสเปกทางเทคนิคของรถจักรยานยนต์ทั้ง 20 รุ่น สำหรับร้าน 160 ธีระ สายซิ่ง
รวบรวมและตรวจสอบตามปีรุ่นและประเภทที่จำหน่าย ข้อมูลที่ไม่สามารถยืนยันได้ระบุชัดเจนว่า "ยังไม่พบข้อมูลยืนยัน"
"""

MOTORCYCLE_SPECS = {
    'BK-FAM-01': {
        'model_name': 'Honda Wave 110i (2024)',
        'price_simulated': 44400.0,
        'engine_cc_display': '109.5 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วน 4 ระดับ',
            'fuel_tank_capacity': '5.0 ลิตร',
            'fuel_consumption': 'ประหยัดน้ำมันสูงสุดประมาณ 76.9 กม./ลิตร (อ้างอิงการทดสอบมาตรฐานของผู้ผลิต)',
            'max_power': '8.9 แรงม้า (PS) ที่ 7,500 รอบ/นาที (โดยประมาณ)',
            'max_torque': '8.7 นิวตัน-เมตร ที่ 5,500 รอบ/นาที (โดยประมาณ)',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '693 × 1,919 × 1,064 มม.',
            'curb_weight': 'ประมาณ 96–99 กก. (ขึ้นอยู่กับรุ่นย่อย ล้อแม็ก/ซี่ลวด/สตาร์ทมือ)',
            'wheelbase': '1,227 มม.',
            'seat_height': '755 มม.',
            'ground_clearance': '132 มม.',
            'storage_capacity': 'ประมาณ 10 ลิตร (U-Box ใต้เบาะ)',
            'lighting': 'ไฟหน้า LED สว่างชัดเจน / ไฟท้ายหลอดฮาโลเจนมาตรฐาน',
            'starter': 'สตาร์ทไฟฟ้าและสตาร์ทเท้า (ขึ้นอยู่กับรุ่นย่อย)'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค (Telescopic)',
            'rear_suspension': 'สวิงอาร์ม โช้คอัพคู่',
            'front_brake': 'ดิสก์เบรกหน้า (รุ่นดิสก์) หรือ ดรัมเบรก (รุ่นเริ่มต้นดรัม)',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'มาตรฐาน ไม่มี ABS/CBS ในรุ่นนี้',
            'front_tire': '70/90-17M/C 38P',
            'rear_tire': '80/90-17M/C 50P'
        },
        'highlights': 'รถครอบครัวขวัญใจคนไทย ขนาดกะทัดรัด ทนทาน ดูแลง่าย ประหยัดน้ำมันระดับแนวหน้า เหมาะกับการเดินทางไปเรียน ทำงาน และใช้ในชีวิตประจำวัน คล่องตัวสูง',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/family/all-new-wave-110i'
    },

    'BK-FAM-02': {
        'model_name': 'Honda Wave 125i (2024)',
        'price_simulated': 55200.0,
        'engine_cc_display': '124.9 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว Smart Engine',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วน 4 ระดับ',
            'fuel_tank_capacity': '5.4 ลิตร',
            'fuel_consumption': 'ประมาณ 71.4 กม./ลิตร (อ้างอิงการทดสอบมาตรฐาน มอก.)',
            'max_power': '9.2 แรงม้า (PS) ที่ 7,500 รอบ/นาที (โดยประมาณ)',
            'max_torque': '10.2 นิวตัน-เมตร ที่ 5,500 รอบ/นาที (โดยประมาณ)',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '717 × 1,931 × 1,090 มม.',
            'curb_weight': 'ประมาณ 101–103 กก. (ขึ้นอยู่กับรุ่นล้อแม็กหรือล้อซี่ลวด)',
            'wheelbase': '1,258 มม.',
            'seat_height': '758 มม.',
            'ground_clearance': '135 มม.',
            'storage_capacity': 'ช่องเก็บของ U-Box ใต้เบาะขนาดใหญ่ 17 ลิตร (ใส่หมวกกันน็อกเต็มใบได้)',
            'lighting': 'ไฟหน้า Full LED สไตล์หรูหรา / ไฟท้าย X-Clusive LED Tail Light',
            'starter': 'สตาร์ทไฟฟ้าและสตาร์ทเท้า'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'สวิงอาร์ม โช้คอัพคู่',
            'front_brake': 'ดิสก์เบรกไฮดรอลิกล้อหน้า',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'มาตรฐาน ไม่มี ABS',
            'front_tire': '70/90-17M/C 38P',
            'rear_tire': '80/90-17M/C 50P'
        },
        'highlights': 'รถครอบครัวระดับพรีเมียม ขับนุ่มนวล กำลังเครื่องยนต์ 125 ซีซี เร่งแซงมั่นใจ ดีไซน์สง่างาม มีช่องใส่ของขนาดใหญ่ 17 ลิตร ตอบโจทย์การเดินทางประจำวันอย่างยอดเยี่ยม',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/family/new-wave-125i'
    },

    'BK-FAM-03': {
        'model_name': 'Honda Dream 100 รุ่นเก่า (คลาสสิก/แค็ตตาล็อก)',
        'price_simulated': 28000.0,
        'engine_cc_display': '97 cc',
        'is_legacy': True,
        'status_tag': 'เลิกจำหน่าย (สำหรับแสดงในแค็ตตาล็อก)',
        'engine': {
            'engine_type': '4 จังหวะ สูบเดี่ยว OHC แนวนอน',
            'valves': '2 วาล์ว',
            'fuel_system': 'คาร์บูเรเตอร์ (ตามเวอร์ชันเดิมของรุ่น)',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วน 4 ระดับ (Rotary Gear)',
            'fuel_tank_capacity': 'ประมาณ 3.6–3.8 ลิตร (อ้างอิงสเปก Dream ทรงคุรุสภา/ตูดเป็ด)',
            'fuel_consumption': 'ยังไม่พบข้อมูลยืนยันผลทดสอบทางการ (ขึ้นอยู่กับการปรับจูนคาร์บูเรเตอร์)',
            'max_power': 'ประมาณ 8.0 แรงม้า ที่ 8,000 รอบ/นาที',
            'max_torque': 'ประมาณ 7.8 นิวตัน-เมตร ที่ 6,000 รอบ/นาที',
            'fuel_type': 'เบนซิน 91 หรือ แก๊สโซฮอล์ 95 (ควรระวังการใช้งานกับ E20)'
        },
        'dimensions': {
            'dimensions_wlh': 'ประมาณ 660 × 1,870 × 1,000 มม. (ตามโครงสร้าง Underbone ยุค 90s)',
            'curb_weight': 'ประมาณ 93–95 กก.',
            'wheelbase': 'ประมาณ 1,180 มม.',
            'seat_height': 'ประมาณ 745 มม.',
            'ground_clearance': 'ประมาณ 130 มม.',
            'storage_capacity': 'ไม่มีกล่อง U-Box ใต้เบาะ (มีตะกร้าหน้ารถตามยุค)',
            'lighting': 'ไฟหน้าทรงเหลี่ยม หลอดไส้ฮาโลเจนดั้งเดิม 12V',
            'starter': 'สตาร์ทเท้าเป็นหลัก (บางรุ่นย่อยมีสตาร์ทมือ)'
        },
        'chassis': {
            'front_suspension': 'แบบขาไก่ Leading Link (รุ่นแรกๆ) หรือ เทเลสโคปิค (รุ่นช่วงท้าย)',
            'rear_suspension': 'สวิงอาร์ม โช้คอัพคู่ ปรับระดับได้',
            'front_brake': 'ดรัมเบรก',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ดรัมเบรกหน้า-หลังคลาสสิก',
            'front_tire': '2.25-17',
            'rear_tire': '2.50-17'
        },
        'highlights': 'ตำนานรถครอบครัวยุคสร้างชาติของคนไทย ทนทาน อะไหล่หาง่าย เหมาะแก่การสะสม ศึกษาประวัติศาสตร์ยานยนต์ ปัจจุบันเป็นรายการแค็ตตาล็อกย้อนยุค ไม่ได้ผลิตจำหน่ายใหม่',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/heritage'
    },

    'BK-FAM-04': {
        'model_name': 'Honda Super Cub 110 (2024)',
        'price_simulated': 48400.0,
        'engine_cc_display': '109.5 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว Smart Engine',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วน 4 ระดับ',
            'fuel_tank_capacity': '4.2 ลิตร',
            'fuel_consumption': 'ประมาณ 65.6–71.4 กม./ลิตร (อ้างอิงผลทดสอบตามมาตรฐาน มอก.)',
            'max_power': '8.0 แรงม้า (PS) ที่ 7,500 รอบ/นาที (โดยประมาณ)',
            'max_torque': '8.8 นิวตัน-เมตร ที่ 5,500 รอบ/นาที (โดยประมาณ)',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '698 × 1,876 × 1,042 มม.',
            'curb_weight': '98 กก.',
            'wheelbase': '1,224 มม.',
            'seat_height': '744 มม.',
            'ground_clearance': '132 มม.',
            'storage_capacity': 'ช่องเก็บของกะทัดรัดใต้ฝาข้าง (สไตล์โมเดิร์นคลาสสิก)',
            'lighting': 'ไฟหน้าทรงกลม Full LED เอกลักษณ์ Super Cub / ไฟเลี้ยวทรงหยดน้ำ',
            'starter': 'สตาร์ทมือและสตาร์ทเท้า'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'สวิงอาร์ม โช้คอัพคู่',
            'front_brake': 'ดรัมเบรก',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ดรัมเบรกหน้า-หลัง สไตล์เรโทรแท้',
            'front_tire': '70/90-17M/C 38P',
            'rear_tire': '80/90-17M/C 50P'
        },
        'highlights': 'รถครอบครัวดีไซน์เจแปนนิสเรโทรคลาสสิกแท้ ไฟหน้าทรงกลม LED ผสานเครื่องยนต์ Smart Engine ทันสมัย ประหยัด คล่องตัว เหมาะกับคนรักแฟชั่นย้อนยุค',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/fashion/new-super-cub'
    },

    'BK-FAM-05': {
        'model_name': 'Yamaha Finn (2024)',
        'price_simulated': 41200.0,
        'engine_cc_display': '114 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว 2 วาล์ว',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีดอัจฉริยะ',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วน 4 ระดับ',
            'fuel_tank_capacity': '4.0 ลิตร',
            'fuel_consumption': 'สูงสุดประมาณ 96.16 กม./ลิตร (อ้างอิงการขับขี่ประหยัดน้ำมันในการทดสอบสื่อ/ผู้ผลิต)',
            'max_power': '8.9 แรงม้า (PS) ที่ 7,000 รอบ/นาที',
            'max_torque': '9.5 นิวตัน-เมตร ที่ 5,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ E10 ถึง E20'
        },
        'dimensions': {
            'dimensions_wlh': '710 × 1,940 × 1,095 มม.',
            'curb_weight': '97–100 กก. (รุ่นล้อซี่ลวด/ล้อแม็ก/UBS)',
            'wheelbase': '1,235 มม.',
            'seat_height': '775 มม.',
            'ground_clearance': '155 มม.',
            'storage_capacity': 'ช่องใส่ของใต้เบาะ 9.7 ลิตร พร้อมช่องใส่ของด้านหน้า',
            'lighting': 'ไฟหน้าฮาโลเจน Diamond Cut สว่างคมชัด / ไฟท้ายโมเดิร์น',
            'starter': 'สตาร์ทมือและสตาร์ทเท้า'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'สวิงอาร์ม โช้คอัพคู่',
            'front_brake': 'ดิสก์เบรกหน้า (รุ่นดิสก์) หรือ ดรัมเบรก (รุ่นสตาร์ทเท้าซี่ลวด)',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบกระจายแรงเบรก UBS (เฉพาะรุ่นท็อป UBS)',
            'front_tire': '70/90-17M/C 38P',
            'rear_tire': '80/90-17M/C 50P'
        },
        'highlights': 'รถครอบครัวสุดคุ้มค่า รับประกัน 5 ปีไม่จำกัดระยะทาง เบาะกว้างนั่งสบาย มีช่องเก็บของด้านหน้า สะดวกในการใช้งาน เหมาะกับนักเรียน นักศึกษา และคนทำงาน',
        'reference_url': 'https://www.yamaha-motor.co.th/commuter/finn-2024/overview'
    },

    'BK-AT-01': {
        'model_name': 'Honda Scoopy (2024)',
        'price_simulated': 49900.0,
        'engine_cc_display': '109.5 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC eSP ระบบจ่ายน้ำมันหัวฉีด PGM-FI',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '4.2 ลิตร',
            'fuel_consumption': 'ประมาณ 55.6 กม./ลิตร (มาตรฐานทดสอบ มอก.)',
            'max_power': '9.0 แรงม้า ที่ 7,500 รอบ/นาที (โดยประมาณ)',
            'max_torque': '9.3 นิวตัน-เมตร ที่ 5,500 รอบ/นาที (โดยประมาณ)',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '683 × 1,864 × 1,076 มม.',
            'curb_weight': '94–95 กก. (รุ่น Club12, Prestige, Urban)',
            'wheelbase': '1,251 มม.',
            'seat_height': '746 มม.',
            'ground_clearance': '147 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะ U-Box 15.4 ลิตร และช่องชาร์จไฟสำรอง USB Type-A',
            'lighting': 'ไฟหน้า Modern Ring LED โดดเด่นเป็นเอกลักษณ์',
            'starter': 'สตาร์ทมือไฟฟ้า (รุ่น Club12 มี Honda Smart Key กุญแจรีโมท)'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ไฮดรอลิก ดิสก์เบรก',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบกระจายแรงเบรก Combi Brake System (CBS)',
            'front_tire': '100/90-12 59J (รุ่นล้อ 12 นิ้ว แบบไม่มียางใน Tubeless)',
            'rear_tire': '110/90-12 64J (รุ่นล้อ 12 นิ้ว แบบไม่มียางใน Tubeless)'
        },
        'highlights': 'ออโตเมติกแฟชั่นยอดนิยม ดีไซน์โค้งมนน่ารัก คล่องตัวในเมือง มีช่องชาร์จมือถือ กุญแจ Smart Key ในรุ่นท็อป ขี่ง่าย ประหยัดน้ำมัน',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/new-scoopy'
    },

    'BK-AT-02': {
        'model_name': 'Honda Click 125i (2024)',
        'price_simulated': 51900.0,
        'engine_cc_display': '124.8 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ (Liquid Cooled)',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '5.5 ลิตร',
            'fuel_consumption': 'ประมาณ 51.5–53.0 กม./ลิตร (มาตรฐานการทดสอบ มอก.)',
            'max_power': '11.1 แรงม้า (PS) ที่ 8,500 รอบ/นาที',
            'max_torque': '10.8 นิวตัน-เมตร ที่ 5,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '679 × 1,918 × 1,066 มม.',
            'curb_weight': '112 กก.',
            'wheelbase': '1,280 มม.',
            'seat_height': '769 มม.',
            'ground_clearance': '132 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะ 18 ลิตร (ใส่หมวกกันน็อกเต็มใบได้)',
            'lighting': 'ไฟหน้า Full LED สไตล์เฉียบคม สปอร์ตเร้าใจ และไฟท้าย LED',
            'starter': 'สตาร์ทมือไฟฟ้า'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้าลูกสูบเดี่ยว',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบ Combi Brake System (CBS)',
            'front_tire': '90/80-14M/C 43P (Tubeless)',
            'rear_tire': '100/80-14M/C 48P (Tubeless)'
        },
        'highlights': 'รถออโตเมติกสปอร์ตยอดนิยม คล่องแคล่ว อัตราเร่งกระฉับกระเฉงด้วยเครื่องยนต์ระบายความร้อนด้วยน้ำ ดีไซน์โฉบเฉี่ยว เหมาะกับคนเมืองที่ต้องการความเร็วและความประหยัด',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/new-click125'
    },

    'BK-AT-03': {
        'model_name': 'Honda Click 150i (2020)',
        'price_simulated': 61200.0,
        'engine_cc_display': '149.3 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย (สต็อกปี 2020)',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ พร้อมหม้อน้ำแบบ Built-in',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '5.5 ลิตร',
            'fuel_consumption': 'ประมาณ 45–48 กม./ลิตร (มาตรฐานการทดสอบโรงงาน)',
            'max_power': '13.1 แรงม้า (PS) ที่ 8,500 รอบ/นาที',
            'max_torque': '13.4 นิวตัน-เมตร ที่ 5,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '679 × 1,919 × 1,062 มม.',
            'curb_weight': '112 กก.',
            'wheelbase': '1,280 มม.',
            'seat_height': '769 มม.',
            'ground_clearance': '132 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะ 18 ลิตร',
            'lighting': 'ไฟหน้า Full LED Dual Headlight / ไฟเลี้ยวแยกส่วนแบบสปอร์ต',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Honda Smart Key'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้า คาลิปเปอร์สีแดงสปอร์ต (รุ่นปี 2020)',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบกระจายแรงเบรก Combi Brake System (CBS)',
            'front_tire': '90/80-14M/C 43P (Tubeless)',
            'rear_tire': '100/80-14M/C 48P (Tubeless)'
        },
        'highlights': 'สปอร์ตออโตเมติกพิกัด 150 ซีซี แรงบิดสูง ออกตัวแรง ดีไซน์คมเข้มดุดัน มาพร้อมระบบสมาร์ทคีย์และหน้าจอ Full Digital Meter ชัดเจน',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/click150i'
    },

    'BK-AT-04': {
        'model_name': 'Honda Click 160 (2024)',
        'price_simulated': 63500.0,
        'engine_cc_display': '156.93 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP+ 4 วาล์ว',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '5.5 ลิตร',
            'fuel_consumption': 'ประมาณ 46.9 กม./ลิตร (มาตรฐาน มอก.)',
            'max_power': '15.4 แรงม้า (PS) ที่ 8,500 รอบ/นาที',
            'max_torque': '13.8 นิวตัน-เมตร ที่ 7,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '678 × 1,929 × 1,088 มม.',
            'curb_weight': '116 กก. (รุ่น Standard) / 118 กก. (รุ่น ABS)',
            'wheelbase': '1,277 มม.',
            'seat_height': '778 มม.',
            'ground_clearance': '138 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะ 18 ลิตร พร้อมช่องชาร์จไฟสำรอง USB Type-A ในช่องคอนโซลหน้า',
            'lighting': 'ไฟหน้า Full LED สปอร์ตระดับไฮเอนด์ และไฟท้าย LED ดีไซน์เอกลักษณ์',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบกุญแจรีโมทอัจฉริยะ Honda SMART Key'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้าไฮดรอลิก',
            'rear_brake': 'ดิสก์เบรกหลัง (รุ่น ABS) หรือ ดรัมเบรก (รุ่น Standard)',
            'brake_system': 'ระบบ Combi Brake System (รุ่น Standard) หรือ Single-channel ABS (รุ่น ABS)',
            'front_tire': '100/80-14M/C 48P (ยาง Tubeless หน้ายางกว้าง)',
            'rear_tire': '120/70-14M/C 61P (ยาง Tubeless หน้ายางกว้าง)'
        },
        'highlights': 'ขุมพลัง eSP+ 4 วาล์ว 157 ซีซี อัตราเร่งทรงพลัง เฟรม eSAF น้ำหนักเบา แข็งแกร่ง ควบคุมง่าย ยางหน้ากว้างเกาะถนนดีเยี่ยม ตอบสนองชีวิตเร่งรีบในเมือง',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/new-click160'
    },

    'BK-AT-05': {
        'model_name': 'Honda PCX 150 รุ่นเก่า (2019 / แค็ตตาล็อก)',
        'price_simulated': 84500.0,
        'engine_cc_display': '149.3 cc',
        'is_legacy': True,
        'status_tag': 'เลิกจำหน่าย (สำหรับแสดงในแค็ตตาล็อก)',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '8.0 ลิตร',
            'fuel_consumption': 'ประมาณ 51.2 กม./ลิตร (อ้างอิงโหมดทดสอบ ECE R40)',
            'max_power': '13.3 แรงม้า ที่ 8,500 รอบ/นาที',
            'max_torque': '13.7 นิวตัน-เมตร ที่ 5,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '745 × 1,923 × 1,107 มม.',
            'curb_weight': '129 กก.',
            'wheelbase': '1,313 มม.',
            'seat_height': '764 มม.',
            'ground_clearance': '137 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะ 28 ลิตร ใส่หมวกกันน็อกเต็มใบได้เหลือเฟือ',
            'lighting': 'ไฟหน้า-ไฟท้าย Full LED พร้อมไฟหรี่ Welcome Light',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Honda Smart Key และกล่องควบคุม Smart Controller'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คอัพคู่',
            'front_brake': 'ดิสก์เบรกหน้า 3 ลูกสูบ พร้อมระบบ Combi Brake',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบ Combi Brake System (CBS)',
            'front_tire': '100/80-14M/C 48P (Tubeless)',
            'rear_tire': '120/70-14M/C 61P (Tubeless)'
        },
        'highlights': 'พรีเมียมเอทีระดับตำนาน เบาะใหญ่นั่งสบาย ถังน้ำมันขนาดใหญ่ 8 ลิตร เดินทางไกลสะดวก ปัจจุบันเป็นรายการแสดงในแค็ตตาล็อกประวัติรุ่นรถ',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/heritage'
    },

    'BK-AT-06': {
        'model_name': 'Honda PCX 160 (2024)',
        'price_simulated': 93400.0,
        'engine_cc_display': '156.93 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP+ 4 วาล์ว',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '8.1 ลิตร',
            'fuel_consumption': 'ประมาณ 45.0–48.5 กม./ลิตร (มาตรฐานการทดสอบ มอก.)',
            'max_power': '15.8 แรงม้า (PS) ที่ 8,500 รอบ/นาที',
            'max_torque': '14.7 นิวตัน-เมตร ที่ 6,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '742 × 1,935 × 1,108 มม.',
            'curb_weight': '131 กก. (รุ่น Standard) / 133 กก. (รุ่น ABS / e:HEV)',
            'wheelbase': '1,313 มม.',
            'seat_height': '764 มม.',
            'ground_clearance': '134 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะขนาดใหญ่พิเศษ 30 ลิตร พร้อมช่องเสียบชาร์จ USB Type-A คอนโซลหน้า',
            'lighting': 'Full LED รอบคัน ไฟหน้าดีไซน์หรูหรา และไฟท้าย 3D LED Shape',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Honda SMART Key'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คอัพคู่ ปรับช่วงยุบให้นุ่มนวลขึ้น',
            'front_brake': 'ดิสก์เบรกไฮดรอลิก',
            'rear_brake': 'ดิสก์เบรกหลัง (มีในรุ่น ABS) หรือ ดรัมเบรก (รุ่น Standard)',
            'brake_system': 'ระบบเบรก ABS หน้า พร้อมระบบควบคุมการลื่นไถล HSTC (เฉพาะรุ่น ABS)',
            'front_tire': '110/70-14M/C 50P (Tubeless)',
            'rear_tire': '130/70-13M/C 63P (Tubeless ล้อหลังขนาด 13 นิ้ว หน้ากว้าง)'
        },
        'highlights': 'ที่สุดของพรีเมียมเอที เครื่องยนต์ eSP+ 4 วาล์ว นุ่ม เงียบ มีระบบ HSTC ป้องกันล้อหมุนฟรี ช่องเก็บของ 30 ลิตร เดินทางไกลสะดวกสบายระดับเฟิร์สคลาส',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/new-pcx160'
    },

    'BK-AT-07': {
        'model_name': 'Honda Lead 125 (2024)',
        'price_simulated': 61500.0,
        'engine_cc_display': '124.8 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว eSP+ 4 วาล์ว',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Matic (CVT)',
            'fuel_tank_capacity': '6.0 ลิตร (ฝาถังน้ำมันอยู่คอนโซลหน้า ไม่ต้องเปิดเบาะ)',
            'fuel_consumption': 'ประมาณ 52.6 กม./ลิตร (มาตรฐาน มอก.)',
            'max_power': '11.0 แรงม้า (PS) ที่ 8,500 รอบ/นาที',
            'max_torque': '11.7 นิวตัน-เมตร ที่ 5,250 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '680 × 1,842 × 1,130 มม.',
            'curb_weight': '113 กก.',
            'wheelbase': '1,273 มม.',
            'seat_height': '760 มม.',
            'ground_clearance': '140 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะยักษ์ U-Box 37 ลิตร (ใหญ่ที่สุดในคลาส จุหมวกเต็มใบได้ 2 ใบ)',
            'lighting': 'ไฟหน้า Full LED ทรง V-Shape สวยงามสะดุดตา',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Honda SMART Key'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้าไฮดรอลิก',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบ Combi Brake System (CBS)',
            'front_tire': '90/90-12 44J (Tubeless)',
            'rear_tire': '100/90-10 56J (Tubeless)'
        },
        'highlights': 'รถออโตเมติกสารพัดประโยชน์ขวัญใจสายขนสัมภาระ U-Box ใหญ่จุใจถึง 37 ลิตร ฝาถังน้ำมันด้านหน้าเติมสะดวก เครื่องยนต์ eSP+ 4 วาล์ว แรง ประหยัด คล่องตัว',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/automatic/new-lead125'
    },

    'BK-AT-08': {
        'model_name': 'Yamaha Fino 115 รุ่นเก่า (คลาสสิก/แค็ตตาล็อก)',
        'price_simulated': 32000.0,
        'engine_cc_display': '113 cc',
        'is_legacy': True,
        'status_tag': 'เลิกจำหน่าย (สำหรับแสดงในแค็ตตาล็อก)',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว 2 วาล์ว',
            'valves': '2 วาล์ว',
            'fuel_system': 'คาร์บูเรเตอร์ (สำหรับรุ่น Fino 115 รุ่นแรกๆ)',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ บังคับด้วยพัดลม',
            'transmission': 'อัตโนมัติ V-Belt',
            'fuel_tank_capacity': '4.1 ลิตร',
            'fuel_consumption': 'ประมาณ 38–43 กม./ลิตร (ขึ้นอยู่กับสภาพการใช้งานและการปรับคาร์บูเรเตอร์)',
            'max_power': 'ประมาณ 7.8 แรงม้า ที่ 8,000 รอบ/นาที',
            'max_torque': 'ประมาณ 8.0 นิวตัน-เมตร ที่ 6,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซิน 91/95 หรือ แก๊สโซฮอล์ 95'
        },
        'dimensions': {
            'dimensions_wlh': '705 × 1,830 × 1,050 มม.',
            'curb_weight': '95 กก.',
            'wheelbase': '1,240 มม.',
            'seat_height': '745 มม.',
            'ground_clearance': '125 มม.',
            'storage_capacity': 'ช่องใส่ของใต้เบาะประมาณ 4.5 ลิตร (ทรงโค้งมนแฟชั่น)',
            'lighting': 'ไฟหน้าทรงตาโตกลมคลาสสิก หลอดฮาโลเจน',
            'starter': 'สตาร์ทมือและสตาร์ทเท้า'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้า',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ดิสก์หน้า/ดรัมหลัง ระบบดั้งเดิม',
            'front_tire': '70/90-14M/C 34P',
            'rear_tire': '80/90-14M/C 40P'
        },
        'highlights': 'ต้นกำเนิดปรากฏการณ์แฟชั่นออโตเมติกทรงเรโทรของเมืองไทย ดีไซน์โค้งมนน่ารัก มีเอกลักษณ์ ปัจจุบันเป็นรถสะสมเพื่อการศึกษาประวัติศาสตร์มอเตอร์ไซค์',
        'reference_url': 'https://www.yamaha-motor.co.th/heritage'
    },

    'BK-AT-09': {
        'model_name': 'Yamaha Grand Filano Hybrid (2024)',
        'price_simulated': 64700.0,
        'engine_cc_display': '125 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC 2 วาล์ว Blue Core พร้อมระบบส่งกำลังไฮบริด',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีดอัจฉริยะ',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'อัตโนมัติ V-Belt',
            'fuel_tank_capacity': '4.4 ลิตร (ฝาถังน้ำมันอยู่ด้านหน้า เติมง่ายไม่ต้องเปิดเบาะ)',
            'fuel_consumption': 'ประหยัดน้ำมันสูงสุดประมาณ 62.5 กม./ลิตร (มาตรฐานการทดสอบของผู้ผลิต)',
            'max_power': '8.2 แรงม้า (PS) ที่ 6,500 รอบ/นาที',
            'max_torque': '10.4 นิวตัน-เมตร ที่ 5,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E10–E20'
        },
        'dimensions': {
            'dimensions_wlh': '685 × 1,820 × 1,155 มม.',
            'curb_weight': '101 กก. (รุ่น STD) / 102 กก. (รุ่น ABS)',
            'wheelbase': '1,280 มม.',
            'seat_height': '790 มม.',
            'ground_clearance': '125 มม.',
            'storage_capacity': 'ช่องเก็บของ Grand Box ใต้เบาะใหญ่ 27 ลิตร พร้อมไฟ LED ส่องสว่าง',
            'lighting': 'Full LED รอบคัน ไฟหน้าทรง Diamond Cut และหน้าจอเรือนไมล์ TFT ดิจิทัล',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Smart Motor Generator นุ่มเงียบ'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คเดี่ยว',
            'front_brake': 'ดิสก์เบรกหน้า',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบ ABS ที่ล้อหน้า (รุ่น ABS) หรือ Unified Brake System - UBS (รุ่น Standard)',
            'front_tire': '110/70-12 47L (Tubeless ยางหน้ากว้าง)',
            'rear_tire': '110/70-12 47L (Tubeless ยางหน้ากว้าง)'
        },
        'highlights': 'พรีเมียมออโตเมติกสไตล์ยุโรป ระบบ Blue Core Hybrid ช่วยส่งกำลังขณะออกตัว ประหยัดน้ำมัน ดีไซน์หรูหรา U-Box ใหญ่ 27 ลิตร ฝาถังน้ำมันด้านหน้าสะดวกสบาย',
        'reference_url': 'https://www.yamaha-motor.co.th/commuter/grand-filano-hybrid-connected-2024/overview'
    },

    'BK-AT-10': {
        'model_name': 'Yamaha Aerox 155 (2024)',
        'price_simulated': 72500.0,
        'engine_cc_display': '155 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC 4 วาล์ว Blue Core พร้อมระบบวาล์วแปรผัน VVA',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีดอัจฉริยะ',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Belt',
            'fuel_tank_capacity': '5.5 ลิตร',
            'fuel_consumption': 'ประมาณ 42–46 กม./ลิตร (มาตรฐานทดสอบการขับขี่สปอร์ต)',
            'max_power': '15.4 แรงม้า (PS) ที่ 8,000 รอบ/นาที',
            'max_torque': '13.9 นิวตัน-เมตร ที่ 6,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซิน หรือ แก๊สโซฮอล์ 91, 95 (รองรับตามคู่มือผู้ผลิต)'
        },
        'dimensions': {
            'dimensions_wlh': '700 × 1,980 × 1,150 มม.',
            'curb_weight': '122 กก. (รุ่น Standard) / 125 กก. (รุ่น ABS)',
            'wheelbase': '1,350 มม.',
            'seat_height': '790 มม.',
            'ground_clearance': '145 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะขนาดใหญ่ 25 ลิตร ใส่หมวกกันน็อกเต็มใบได้',
            'lighting': 'Full LED รอบคัน สไตล์สปอร์ตโฉบเฉี่ยวพร้อม Daytime Running Light',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อมระบบ Smart Key (รุ่น ABS)'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คอัพคู่ พร้อมซับแทงค์ (รุ่น ABS) / โช้คคู่มาตรฐาน (รุ่น STD)',
            'front_brake': 'ดิสก์เบรกหน้า',
            'rear_brake': 'ดรัมเบรก',
            'brake_system': 'ระบบเบรก ABS ที่ล้อหน้า (เฉพาะรุ่น ABS) / ระบบมาตรฐาน (รุ่น STD)',
            'front_tire': '110/80-14M/C 53P (Tubeless)',
            'rear_tire': '140/70-14M/C 62P (Tubeless หน้ายางใหญ่สไตล์สปอร์ต)',
        },
        'highlights': 'สปอร์ตออโตเมติกสายพันธุ์เรซซิ่ง เครื่องยนต์ Blue Core 155 ซีซี วาล์วแปรผัน VVA แรงทุกย่านความเร็ว ยางหลังใหญ่ 140 มม. ทรงตัวแน่น เกาะถนนมั่นใจ',
        'reference_url': 'https://www.yamaha-motor.co.th/commuter/aerox-155-2024/overview'
    },

    'BK-AT-11': {
        'model_name': 'Yamaha NMAX 155 (2024)',
        'price_simulated': 92900.0,
        'engine_cc_display': '155 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC 4 วาล์ว Blue Core พร้อมระบบวาล์วแปรผัน VVA',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีดอัจฉริยะ',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'อัตโนมัติ V-Belt',
            'fuel_tank_capacity': '7.1 ลิตร',
            'fuel_consumption': 'ประมาณ 40–45 กม./ลิตร (มาตรฐานการทดสอบ)',
            'max_power': '15.4 แรงม้า (PS) ที่ 8,000 รอบ/นาที',
            'max_torque': '13.9 นิวตัน-เมตร ที่ 6,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95'
        },
        'dimensions': {
            'dimensions_wlh': '740 × 1,935 × 1,160 มม.',
            'curb_weight': '131 กก.',
            'wheelbase': '1,340 มม.',
            'seat_height': '765 มม.',
            'ground_clearance': '125 มม.',
            'storage_capacity': 'ช่องเก็บของใต้เบาะขนาดใหญ่ 23.3 ลิตร พร้อมที่วางเท้า 2 ท่าทางเหยียดสบาย',
            'lighting': 'ไฟหน้า-ไฟท้าย Full LED พร้อมระบบเชื่อมต่อ Y-Connect (ในรุ่น Connected)',
            'starter': 'สตาร์ทมือไฟฟ้า พร้อม Smart Key System'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค',
            'rear_suspension': 'ยูนิตสวิง โช้คอัพคู่ ซับแทงค์ปรับได้',
            'front_brake': 'ดิสก์เบรกหน้า',
            'rear_brake': 'ดิสก์เบรกหลัง',
            'brake_system': 'ระบบ Dual Channel ABS (หน้า-หลัง) พร้อมระบบ Traction Control System (TCS)',
            'front_tire': '110/70-13M/C 48P (Tubeless)',
            'rear_tire': '130/70-13M/C 63P (Tubeless)'
        },
        'highlights': 'พรีเมียมสปอร์ตสกู๊ตเตอร์ตระกูล MAX Series ความสบายระดับทัวร์ริ่ง ดิสก์เบรกหน้า-หลัง พร้อม ABS 2 ล้อ และ Traction Control เพิ่มความปลอดภัยสูงสุด',
        'reference_url': 'https://www.yamaha-motor.co.th/commuter/nmax-155-2024/overview'
    },

    'BK-SPT-01': {
        'model_name': 'Honda MSX 125 (Grom 125 / 2021)',
        'price_simulated': 71000.0,
        'engine_cc_display': '124 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC สูบเดี่ยว คลัตช์มือ',
            'valves': '2 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยอากาศ',
            'transmission': 'เกียร์วนคลัตช์มือ 5 สปีด (Manual Clutch 5-Speed)',
            'fuel_tank_capacity': '6.0 ลิตร',
            'fuel_consumption': 'ประมาณ 65.7 กม./ลิตร (มาตรฐานการทดสอบโรงงาน)',
            'max_power': '9.8 แรงม้า (PS) ที่ 7,250 รอบ/นาที',
            'max_torque': '10.5 นิวตัน-เมตร ที่ 5,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '722 × 1,758 × 1,017 มม.',
            'curb_weight': '103 กก. (รุ่น STD) / 104 กก. (รุ่น ABS G-Sensor)',
            'wheelbase': '1,198 มม.',
            'seat_height': '761 มม.',
            'ground_clearance': '178 มม.',
            'storage_capacity': 'ไม่มีช่อง U-Box (เป็นรถมินิไบค์สปอร์ต)',
            'lighting': 'ไฟหน้า Full LED ทรงสปอร์ตและหน้าจอเรือนไมล์ดิจิทัลเต็มรูปแบบพร้อมไฟบอกตำแหน่งเกียร์',
            'starter': 'สตาร์ทมือไฟฟ้า'
        },
        'chassis': {
            'front_suspension': 'โช้คหน้าหัวกลับ Upside-Down ขนาด 31 มม.',
            'rear_suspension': 'สวิงอาร์ม โช้คเดี่ยว (Monoshock)',
            'front_brake': 'ดิสก์เบรกไฮดรอลิกหน้า จานเบรก 220 มม.',
            'rear_brake': 'ดิสก์เบรกไฮดรอลิกหลัง จานเบรก 190 มม.',
            'brake_system': 'ดิสก์เบรกหน้า-หลัง พร้อมรุ่น ABS เทคโนโลยี G-Sensor ป้องกันท้ายยก',
            'front_tire': '120/70-12 51L (Tubeless)',
            'rear_tire': '130/70-12 56L (Tubeless)'
        },
        'highlights': 'มินิไบค์สตรีทไฟเตอร์ขี่สนุก เกียร์ 5 สปีดพร้อมคลัตช์มือ โช้คหน้าหัวกลับ Upside-Down ถอดเปลี่ยนฝาครอบแต่ง DIY ได้ง่าย โดนใจวัยรุ่น',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/minibike/new-grom'
    },

    'BK-SPT-02': {
        'model_name': 'Honda CBR150R (2024)',
        'price_simulated': 99900.0,
        'engine_cc_display': '149.16 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ DOHC 4 วาล์ว สูบเดี่ยว ระบายความร้อนด้วยน้ำ',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีด PGM-FI',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'เกียร์ธรรมดา 6 ระดับ คลัตช์มือ พร้อม Assist Slipper Clutch',
            'fuel_tank_capacity': '12.0 ลิตร',
            'fuel_consumption': 'ประมาณ 39–43 กม./ลิตร (มาตรฐานการขับขี่สปอร์ต)',
            'max_power': '17.1 แรงม้า (PS) ที่ 9,000 รอบ/นาที',
            'max_torque': '14.4 นิวตัน-เมตร ที่ 7,000 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E20'
        },
        'dimensions': {
            'dimensions_wlh': '700 × 1,983 × 1,090 มม.',
            'curb_weight': '137 กก. (รุ่น Non-ABS) / 139 กก. (รุ่น ABS)',
            'wheelbase': '1,310 มม.',
            'seat_height': '788 มม.',
            'ground_clearance': '151 มม.',
            'storage_capacity': 'ช่องใส่เอกสารและเครื่องมือขนาดเล็กใต้เบาะคนซ้อน',
            'lighting': 'Full LED รอบคัน ไฟหน้าคู่ทรงสปอร์ตถ่ายทอด DNA จาก CBR ซูเปอร์สปอร์ต',
            'starter': 'สตาร์ทมือไฟฟ้า'
        },
        'chassis': {
            'front_suspension': 'โช้คหน้าหัวกลับ Upside-Down จาก Showa ขนาดแกน 37 มม.',
            'rear_suspension': 'สวิงอาร์ม โช้คเดี่ยว Pro-Link ปรับพรีโหลดได้ 5 ระดับ',
            'front_brake': 'เวฟดิสก์เบรกหน้า ไฮดรอลิก',
            'rear_brake': 'เวฟดิสก์เบรกหลัง ไฮดรอลิก',
            'brake_system': 'ระบบเบรก ABS หน้า-หลัง พร้อมสัญญาณไฟฉุกเฉินกะพริบอัตโนมัติ ESS (ในรุ่น ABS)',
            'front_tire': '100/80-17M/C 52P (Tubeless)',
            'rear_tire': '130/70-17M/C 62P (Tubeless)'
        },
        'highlights': 'รถสปอร์ตฟูลแฟริ่งเรซซิ่ง DNA เครื่องยนต์ DOHC 4 วาล์ว เกียร์ 6 สปีด มี Assist Slipper Clutch ป้องกันล้อล็อกขณะเชนจ์เกียร์ และโช้คหัวกลับ Showa มั่นใจทุกโค้ง',
        'reference_url': 'https://www.thaihonda.co.th/honda/motorcycle/sport/all-new-cbr150r'
    },

    'BK-SPT-03': {
        'model_name': 'Yamaha R15 (2024)',
        'price_simulated': 118000.0,
        'engine_cc_display': '155 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ SOHC 4 วาล์ว พร้อมระบบวาล์วแปรผัน VVA',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีดอัจฉริยะ',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ',
            'transmission': 'เกียร์สปอร์ต 6 ระดับ พร้อม Assist & Slipper Clutch',
            'fuel_tank_capacity': '11.0 ลิตร',
            'fuel_consumption': 'ประมาณ 40–45 กม./ลิตร (มาตรฐานการทดสอบ)',
            'max_power': '18.4 แรงม้า (PS) ที่ 10,000 รอบ/นาที',
            'max_torque': '14.2 นิวตัน-เมตร ที่ 8,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95, E10–E20'
        },
        'dimensions': {
            'dimensions_wlh': '725 × 1,990 × 1,135 มม.',
            'curb_weight': '137 กก. (รุ่น Connected) / 140 กก. (รุ่น R15M Connected-ABS)',
            'wheelbase': '1,325 มม.',
            'seat_height': '815 มม.',
            'ground_clearance': '170 มม.',
            'storage_capacity': 'ช่องใส่ชุดเครื่องมือช่างขนาดเล็กใต้เบาะหลัง',
            'lighting': 'ไฟหน้าโมโนโฟกัส LED ตรงกลาง พร้อม LED Daytime Running Light ไฟเลี้ยวสปอร์ต',
            'starter': 'สตาร์ทมือไฟฟ้า'
        },
        'chassis': {
            'front_suspension': 'โช้คหัวกลับ Upside-Down สีทอง/น้ำเงิน',
            'rear_suspension': 'สวิงอาร์มอลูมิเนียม โช้คเดี่ยว Link-Type',
            'front_brake': 'ดิสก์เบรกหน้า จานเบรกขนาด 282 มม.',
            'rear_brake': 'ดิสก์เบรกหลัง จานเบรกขนาด 220 มม.',
            'brake_system': 'ระบบ Dual Channel ABS, Traction Control System และ Quick Shifter (ในรุ่น R15M)',
            'front_tire': '100/80-17M/C 52P (Tubeless)',
            'rear_tire': '140/70-17M/C 66H (Tubeless)'
        },
        'highlights': 'ซูเปอร์สปอร์ตคลาส 150 ถ่ายทอด DNA จาก YZR-M1 รถแข่ง MotoGP กำลัง 18.4 แรงม้า สวิงอาร์มหลังอลูมิเนียม พร้อม Quick Shifter ในรุ่น R15M สุดยอดความสปอร์ต',
        'reference_url': 'https://www.yamaha-motor.co.th/commuter/r15-connected-2024/overview'
    },

    'BK-SPT-04': {
        'model_name': 'Suzuki Raider R150 (2023)',
        'price_simulated': 69900.0,
        'engine_cc_display': '147 cc',
        'is_legacy': False,
        'status_tag': 'มีจำหน่าย',
        'engine': {
            'engine_type': '4 จังหวะ DOHC 4 วาล์ว Twincam สูบเดี่ยว',
            'valves': '4 วาล์ว',
            'fuel_system': 'หัวฉีดแบบ 2-Spray ทวินเจ็ท',
            'cooling_system': 'ระบายความร้อนด้วยน้ำ (Liquid Cooled พร้อมหม้อน้ำขนาดใหญ่)',
            'transmission': 'เกียร์ธรรมดา คลัตช์มือ 6 สปีด',
            'fuel_tank_capacity': '4.0 ลิตร',
            'fuel_consumption': 'ประมาณ 38–42 กม./ลิตร (ขึ้นอยู่กับรูปแบบการขับขี่รอบสูง)',
            'max_power': '18.2 แรงม้า (PS) ที่ 10,000 รอบ/นาที',
            'max_torque': '13.8 นิวตัน-เมตร ที่ 8,500 รอบ/นาที',
            'fuel_type': 'น้ำมันเบนซินไร้สารตะกั่ว หรือ แก๊สโซฮอล์ 91, 95 (อัตราส่วนกำลังอัด 11.5:1)'
        },
        'dimensions': {
            'dimensions_wlh': '675 × 1,960 × 980 มม.',
            'curb_weight': '111 กก.',
            'wheelbase': '1,280 มม.',
            'seat_height': '765 มม.',
            'ground_clearance': '150 มม.',
            'storage_capacity': 'ช่องใส่ของอเนกประสงค์ขนาดเล็กบริเวณคอนโซลกลาง',
            'lighting': 'ไฟหน้า Full LED สไตล์เฉียบคม และหน้าจอดิจิทัล Full LCD',
            'starter': 'สตาร์ทมือไฟฟ้าด้วยระบบ Suzuki Easy Start System'
        },
        'chassis': {
            'front_suspension': 'เทเลสโคปิค คอยล์สปริง ออยล์แดมป์เปอร์',
            'rear_suspension': 'สวิงอาร์ม โช้คเดี่ยว (Monoshock)',
            'front_brake': 'ดิสก์เบรกหน้า จานดิสก์ขนาดใหญ่แบบ Petal Disc',
            'rear_brake': 'ดิสก์เบรกหลัง',
            'brake_system': 'ดิสก์เบรกหน้า-หลัง ไม่มีระบบ ABS',
            'front_tire': '70/90-17M/C 38P (Tubed/ยางใน)',
            'rear_tire': '80/90-17M/C 50P (Tubed/ยางใน)'
        },
        'highlights': 'ราชาแห่งรถกะเทยสายซิ่ง Hyper Underbone เครื่องยนต์ทวินแคม DOHC 4 วาล์ว 18.2 แรงม้า ตัวถังเพรียวน้ำหนักเพียง 111 กก. อัตราเร่งจัดจ้านที่สุดในกลุ่ม Underbone',
        'reference_url': 'https://www.suzukimotosales.co.th/motorcycle/raider-r150/'
    }
}
