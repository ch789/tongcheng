#!/usr/bin/env python3
"""MVP 测试数据录入：生成类目匹配的图（PIL），落地 api/uploads/admin，再写库。
- 轮播图 6 张（ads）
- 产品 6 个（products，industry 对应）
- 活动 6 个（activities，图文合主题）
图片字段统一存相对路径 /uploads/admin/<name>，dev 同域下可显示；
本地 BASE_URL=http://localhost:8000，跨域时前端 resolveAsset 会自动补域。
"""
import os, json, hashlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))   # api/
UPLOAD = os.path.join(ROOT, "uploads", "admin")
os.makedirs(UPLOAD, exist_ok=True)
FONT = "/System/Library/Fonts/PingFang.ttc"
DB = "handanzh"
BASE_REL = "/uploads/admin/"

def psql(sql):
    r = subprocess.run(
        ["docker","exec","handanzh-db","psql","-U","postgres","-d",DB,"-c",sql],
        capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def save(name, w, h, top, bottom, lines, taglines):
    """生成一张图：顶部色带+标题，中部插画几何，底部说明文字。"""
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    # 顶部渐变色块
    d.rectangle([0,0,w,int(h*0.30)], fill=top)
    # 几何装饰（半透圆形模拟插画）
    import random
    random.seed(name)
    for _ in range(4):
        cx=random.randint(0,w); cy=random.randint(0,h//2); rr=random.randint(30,90)
        d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr], outline=bottom, width=3)
    # 标题（顶部）
    f_title = ImageFont.truetype(FONT, int(h*0.06))
    f_body  = ImageFont.truetype(FONT, int(h*0.032))
    d.text((int(w*0.06), int(h*0.10)), taglines[0], fill="white", font=f_title)
    # 中部大标签（列表不足时留空，容错）
    f_big = ImageFont.truetype(FONT, int(h*0.05))
    if len(taglines) > 1:
        d.text((int(w*0.06), int(h*0.40)), taglines[1], fill=bottom, font=f_big)
    # 底部说明
    y = int(h*0.62)
    for ln in lines:
        d.text((int(w*0.06), y), ln, fill="#333", font=f_body)
        y += int(h*0.055)
    p = os.path.join(UPLOAD, name)
    img.save(p, "JPEG", quality=82)
    return BASE_REL + name

def now_sql(offset_days, hour=10):
    # 固定时间戳，避免依赖当前日期
    return offset_days, hour

def run():
    # ── 行业 id 映射（与库一致） ──
    ind = {"餐饮美食":1,"装修建材":2,"家政服务":3,"教育培训":4,"法律服务":5,
           "医疗健康":6,"汽车服务":7,"商贸批发":8,"休闲娱乐":9,"房产服务":10,
           "美容美发":11,"物流快递":12}

    # ── 幂等清理：删掉上次按本次图名造的数据，避免重跑堆叠 ──
    psql("delete from ads where image like '%/ad_%';")
    psql("delete from products where images::text like '%prod_%';")
    psql("delete from activities where cover_image like '%/ev_%';")
    # 清掉上次生成的图片文件
    import glob
    for f in glob.glob(os.path.join(UPLOAD, "ad_*.jpg")) + \
             glob.glob(os.path.join(UPLOAD, "prod_*.jpg")) + \
             glob.glob(os.path.join(UPLOAD, "ev_*.jpg")):
        os.remove(f)

    # ── 1) 轮播图 6 张 ──
    ads = [
        ("同城老乡服务平台 正式上线","在津在外的老乡，找商户、找活动、找同乡服务",
         ["平台新上线，注册即享专属服务","覆盖餐饮·家政·教育·医疗等 12 大行业"],
         "#1a73e8","#4a9af5","ad_platform"),
        ("老字号餐饮 老乡推荐","邯郸特色面食、酱香肉，老味道新体验",
         ["凭平台注册可享首单 9 折","支持预约堂食 / 到店自提"],
         "#c0392b","#e67e22","ad_food"),
        ("同乡互助 家政上门","同城家政·保洁·维修，老乡之间更放心",
         ["实名认证阿姨，48h 内上门","满意可在线好评返现"],
         "#16a085","#1abc9c","ad_home"),
        ("教育培训 寒期班","本地优质课程，老师推荐、口碑优先",
         ["课程试听免费，名额有限","报名即送学习礼包"],
         "#8e44ad","#c2185b","ad_edu"),
        ("医疗健康 体检优惠","同乡专属体检套餐，预约更方便",
         ["含全项检查，报告 3 日出","支持在线预约、家人代约"],
         "#2c3e50","#3498db","ad_med"),
        ("休闲娱乐 同城好去处","周末同乡聚会、亲子活动报名",
         ["活动报名免费，名额先到先得","现场扫码签到即入场"],
         "#d35400","#f39c12","ad_leisure"),
    ]
    ad_rows=[]
    for i,(title,tag,lines,c1,c2,fname) in enumerate(ads):
        # 轮播：H5 banner 框 375×150（2.5:1）→ 图用 1200×480 贴满不裁
        img = save(f"{fname}.jpg", 1200, 480, c1, c2, lines, [title, tag])
        ad_rows.append(dict(title=title, image=img, sort_order=i+1))

    # ── 2) 产品 6 个（industry 对应） ──
    products = [
        ("老字号·酱香肉夹馍","精选五花肉慢炖 8 小时，配现烤馍，口感酥嫩。营业时间 09:00-21:00，可外卖。",
         "餐饮美食","#c0392b","prod_roujiamo","13800001111"),
        ("全屋定制 环保板材","E0 级环保板材，10 年质保，免费上门量房出方案，适合新装 / 旧改。",
         "装修建材","#16a085","prod_cabinet","13800002222"),
        ("家政深度保洁 3 小时","标准 3 小时全屋深度清洁，含厨卫除垢，可加选除螨、收纳整理。",
         "家政服务","#8e44ad","prod_jingjie","13800003333"),
        ("少儿编程启蒙 8-12 岁","图形化编程入门，小班教学，周末班 / 晚班可选，试听免费。",
         "教育培训","#2c3e50","prod_coding","13800004444"),
        ("全项体检套餐 128 项","含血尿便常规、肝肾功能、心电图、彩超，报告 3 日出具。",
         "医疗健康","#1abc9c","prod_tijian","13800005555"),
        ("同城急送 2 小时达","专人直送，同城 2 小时内送达，贵重物品可保价，7×24 接单。",
         "物流快递","#d35400","prod_kuaidi","13800006666"),
    ]
    prod_rows=[]
    for title,desc,iname,c1,fname,phone in products:
        # 产品：H5 卡片框 375×120（3.1:1）/ 详情 375×300 → 取 1200×560（≈2.14:1）宽图，
        # 卡片 cover 裁切最小、详情整图可见。分辨率提上去避免放大糊。
        img = save(f"{fname}.jpg", 1200, 560, c1, "#f0f0f0", [title], [desc[:16]+"…"])
        prod_rows.append(dict(title=title, description=desc, industry_id=ind[iname],
                              images=[img], contact_phone=phone, area="市区"))

    # ── 3) 活动 6 个（图文合主题） ──
    acts = [
        ("老乡周末聚餐会","老地方老味道，周六晚上同城老乡一起吃饭唠唠，欢迎新面孔。到场扫码签到。",
         "市区老馆子","upcoming","#c0392b","ev_dinner"),
        ("同乡亲子户外野餐","周日公园亲子活动，含野餐 + 亲子游戏 + 拍照打卡，限 30 组家庭。",
         "滨江公园","registering","#27ae60","ev_family"),
        ("本地商户资源对接会","在津经商的老乡交流资源、对接生意，餐饮/建材/服务业均可参加。",
         "会展中心 3 号厅","registering","#2980b9","ev_biz"),
        ("社区义诊 · 免费体检","邀请同乡一起给社区做健康义诊，测量血压血糖、咨询问诊。",
         "社区服务中心","upcoming","#1abc9c","ev_yizhen"),
        ("老乡才艺秀 报名中","月底同乡才艺展示，唱歌 / 乐器 / 舞蹈均可，报名即抽奖品。",
         "市民礼堂","upcoming","#8e44ad","ev_shou"),
        ("端午同乡龙舟赛","去年举办，报名火爆，照片留念。下届继续筹备。",
         "南郊湖","ended","#d35400","ev_loong"),
    ]
    act_rows=[]
    for title,content,loc,status,c1,fname in acts:
        # 活动：封面框 375×220（1.7:1）/ 卡片方框 90×90 → 取 1200×700（≈1.7:1）宽图，
        # 详情 cover 裁切最小、整图可见
        img = save(f"{fname}.jpg", 1200, 700, c1, "#f5f5f5", [content[:18]+"…"], [title])
        act_rows.append(dict(title=title, cover_image=img, location=loc, status=status,
                             content=content, max_participants=50))

    # ── 写库 ──
    # 广告
    for r in ad_rows:
        sql=f"""insert into ads(title,image,link,merchant_id,sort_order,status,created_at)
                values ('{r['title']}','{r['image']}',NULL,NULL,{r['sort_order']},'ACTIVE',now()) returning id;"""
        psql(sql); print("AD", r["title"])
    # 产品（merchant_id 用 admin 的 id=1）
    for r in prod_rows:
        imgs = "'{" + ",".join(r["images"]) + "}'"
        sql=f"""insert into products(merchant_id,title,description,images,industry_id,area,contact_phone,view_count,status,created_at,updated_at)
                values (1,'{r['title']}','{r['description']}',{imgs},{r['industry_id']},'{r['area']}','{r['contact_phone']}',0,'APPROVED',now(),now()) returning id;"""
        psql(sql); print("PRODUCT", r["title"])
    # 活动（时间：upcoming 未来、registering 进行中、ended 过去）
    import datetime
    today = datetime.date(2026,9,24)
    status_upper = {"upcoming":"UPCOMING","registering":"REGISTERING","ended":"ENDED"}
    for r in act_rows:
        st = r["status"]
        if st=="ended":
            s,e = today-datetime.timedelta(days=60), today-datetime.timedelta(days=58)
        elif st=="registering":
            s,e = today, today+datetime.timedelta(days=7)
        else:
            s,e = today+datetime.timedelta(days=14), today+datetime.timedelta(days=16)
        sdt = f"{s.isoformat()} 09:00:00"
        edt = f"{e.isoformat()} 21:00:00"
        sql=f"""insert into activities(title,cover_image,start_time,end_time,location,content,max_participants,status,created_at)
                values ('{r['title']}','{r['cover_image']}',
                '{sdt}','{edt}',
                '{r['location']}','{r['content']}',{r['max_participants']},'{status_upper[st]}',now()) returning id;"""
        psql(sql); print("ACTIVITY", r["title"], st, "→", status_upper[st])
    print("\nDONE")

if __name__=="__main__":
    run()
