import streamlit as st
import calendar
from utils import *
from streamlit_calendar import calendar as cdar
import pandas as pd
st.set_page_config(layout="wide")

# 상태 초기화 (멤버 리스트가 없다면 초기화)
if "members" not in st.session_state:
    st.session_state["members"] = []

if "last_month" not in st.session_state:
    st.session_state["last_month"] = None

if "no_date" not in st.session_state:
    st.session_state["no_date"] = []

if "schedule_generated" not in st.session_state:
    st.session_state["schedule_generated"] = False
    
if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = False

# 해당 월의 일수를 계산
def get_day_options(year, month):
    _, num_days = calendar.monthrange(year, month)
    return [f"{month}/{day}" for day in range(1, num_days + 1)]


# 요일과 시간(5시, 7시) 옵션 만들기
weekday_time_options = [
    f"{weekday}{time}"
    for weekday in ["월", "화", "수", "목", "금"]
    for time in ["5", "7"]
]


# 멤버 추가 버튼 클릭 시 빈 입력 행 추가
def add_member():
    st.session_state["members"].append(
        {
            "name": "",
            "Priority": 1,
            "ImpossibleWeekday": [],
            "ImpossibleDay": [],
            "PreferredWeekday": [],
            "PreferredDay": [],
            "MustDay": [],
        }
    )


# 멤버 삭제
def delete_member(index):
    st.session_state["members"].pop(index)


# 년도와 월 선택 (한 줄로 배치)
cols = st.columns([1, 1])

with cols[0]:
    year = st.selectbox("년도 선택", range(2020, 2031), index=0)

with cols[1]:
    month = st.selectbox("월 선택", range(1, 13), index=0)

# 사용자가 년도와 월을 선택한 경우만 멤버 입력 행을 추가
if year != 2020 and month != 1:
    day_options = get_day_options(year, month)
    st.session_state["last_month"] = month
    st.multiselect(f"이번 달에 제외할 날짜",
                day_options,
                default=st.session_state["no_date"],
                key=f"no_date",
            )
    if len(st.session_state["members"]) == 0:
        add_member()  # 선택된 월에 대해 첫 번째 입력 행 추가


# 멤버 리스트 렌더링 (년도와 월 선택 후만 렌더링)
if st.session_state["members"]:
    for idx, member in enumerate(st.session_state["members"]):
        cols = st.columns([1, 1, 2, 2, 2, 2, 2, 1])  # 한 줄에 여러 칼럼 배치

        with cols[0]:
            st.session_state["members"][idx]["name"] = st.text_input(
                f"이름",
                value=st.session_state["members"][idx]["name"],
                key=f"name_{idx}",
            )

        with cols[1]:
            st.session_state["members"][idx]["Priority"] = st.selectbox(
                f"우선 순위",
                [1, 2, 3],
                index=st.session_state["members"][idx]["Priority"] - 1,
                key=f"priority_{idx}",
            )

        with cols[2]:
            impossible_weekday = st.multiselect(
                f"불가능 요일",
                weekday_time_options,
                key=f"impossible_weekday_{idx}",
            )

        with cols[3]:
            impossible_day = st.multiselect(
                f"불가능 날짜",
                day_options,
                key=f"impossible_day_{idx}",
            )

        with cols[4]:
            preferred_weekday = st.multiselect(
                f"선호 요일",
                weekday_time_options,
                key=f"preferred_weekday_{idx}",
            )

        with cols[5]:
            preferred_day = st.multiselect(
                f"선호 날짜",
                day_options,
                key=f"preferred_day_{idx}",
            )

        with cols[6]:
            must_day = st.multiselect(
                f"반드시 해야 하는 날짜",
                day_options,
                key=f"must_day_{idx}",
            )

        # 상태 한 번에 업데이트
        st.session_state["members"][idx]["ImpossibleWeekday"] = impossible_weekday
        st.session_state["members"][idx]["ImpossibleDay"] = impossible_day
        st.session_state["members"][idx]["PreferredWeekday"] = preferred_weekday
        st.session_state["members"][idx]["PreferredDay"] = preferred_day
        st.session_state["members"][idx]["MustDay"] = must_day

        # 삭제 버튼
        with cols[7]:
            st.write("")
            if st.button("삭제", key=f"delete_{idx}"):
                delete_member(idx)
                st.rerun()  # 삭제 후 새로고침

# 버튼을 한 줄로 배치 (추가 버튼과 확인 버튼)
button_cols = st.columns([1, 1,17])

if st.button("추가"):
    add_member()
    st.rerun()


# 버튼 클릭 시 클릭 상태를 저장
if st.button("시간표 생성"):
    st.session_state["button_clicked"] = True
    members_dict = convert_members_to_dict(st.session_state["members"])
    calendar_info_list = generate_calendar_info(year, month, st.session_state["no_date"])
    sorted_names = sort_members_by_criteria(members_dict)
    solution = []
    backtracking(solution, sorted_names, 0, calendar_info_list, [], members_dict, len(members_dict))
    
    # 결과 상태 저장
    st.session_state["solution"] = solution
    
    # 보기 좋은 형태로 출력하기 위해 데이터를 변환
    formatted_solution = []
    for entry in st.session_state["solution"]:
        member_name = entry[0]
        event_info = entry[1]
        year, month, day, time_slot = event_info
        formatted_solution.append({
            "이름": member_name,
            "연도": year,
            "월": month,
            "일": day,
            "시간대": time_slot
        })
    
    # DataFrame으로 변환하여 출력
    df = pd.DataFrame(formatted_solution)
    st.table(df)  # 테이블 형식으로 출력