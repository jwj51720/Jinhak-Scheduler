import calendar

def convert_members_to_dict(members):
    members_dict = {}
    for member in members:
        name = member["name"]
        if name:  # 이름이 비어있지 않을 경우만 추가
            members_dict[name] = {
                "Priority": member["Priority"],
                "ImpossibleWeekday": member["ImpossibleWeekday"],
                "ImpossibleDay": member["ImpossibleDay"],
                "PreferredWeekday": member["PreferredWeekday"],
                "PreferredDay": member["PreferredDay"],
                "MustDay": member["MustDay"],
            }
    return members_dict


def generate_calendar_info(year, month, global_impossible_date):
    # 해당 연도와 월의 시작 요일과 일수를 가져옴
    start_day, num_days = calendar.monthrange(year, month)

    # 요일 dict
    weekday_dict = {
        0: '월',
        1: '화',
        2: '수',
        3: '목',
        4: '금',
        5: '토',
        6: '일'
    }

    # 해당 월의 [년, 달, 일, 요일] 정보를 담은 리스트 생성
    calendar_info_5 = []  # 5일 정보 리스트
    calendar_info_7 = []  # 7일 정보 리스트
    
    for day in range(1, num_days + 1):
        weekday = (start_day + (day - 1)) % 7  # 해당 일의 요일 계산
        # "11/23" 같은 형식으로 변환한 후, global_impossible_date에 포함되면 제외
        date_str = f"{month}/{day}"
        if weekday_dict[weekday] not in ['토', '일'] and date_str not in global_impossible_date:
            # 5일 정보 먼저 추가
            day_info_5 = [year, month, day, weekday_dict[weekday] + "5"]
            calendar_info_5.append(day_info_5)
            # 7일 정보 나중에 추가
            day_info_7 = [year, month, day, weekday_dict[weekday] + "7"]
            calendar_info_7.append(day_info_7)

    # 5일 정보 리스트와 7일 정보 리스트를 합침
    calendar_info = calendar_info_7 + calendar_info_5
    calendar_info.reverse()  # 역순 정렬
    return calendar_info

def sort_members_by_criteria(members):
    # 1. MustDay가 있는지 확인하는 기준
    def has_must_day(member_data):
        return len(member_data['MustDay']) > 0

    # 2. ImpossibleWeekday가 적은지 확인하는 기준
    def count_impossible_weekdays(member_data):
        return len(member_data['ImpossibleWeekday'])

    # 정렬 기준: MustDay > Priority > ImpossibleWeekday
    sorted_members = sorted(
        members.items(),
        key=lambda item: (
            not has_must_day(item[1]),  # MustDay가 있는 학생을 앞으로 (True -> False로 정렬)
            item[1]['Priority'],         # 우선순위가 낮은 수치가 앞으로 (1 -> 2 -> 3)
            count_impossible_weekdays(item[1])  # ImpossibleWeekday가 적은 학생이 앞으로
        )
    )

    # 이름 리스트만 추출하여 반환
    sorted_names = [name for name, _ in sorted_members]
    return sorted_names

def is_valid(solution, member, date, condition):
    # 불가능한 날짜에 해당하는 경우
    for day2 in condition[member]["ImpossibleDay"]:
        month, day = map(int, day2.split("/"))
        if month in date and day in date:
            return False
    
    # 불가능한 요일과 시간에 해당하는 경우
    for weekday in condition[member]["ImpossibleWeekday"]:
        if weekday in date:
            return False
    
    # 반드시 해야 하는 날짜에 해당하는 경우
    for day2 in condition[member]["MustDay"]:
        month, day = map(int, day2.split("/"))
        if month in date and day in date:
            return True
    
    # 선호하는 날짜에 해당하는 경우
    for day2 in condition[member]["PreferredDay"]:
        month, day = map(int, day2.split("/"))
        if month in date and day in date:
            return True
    
    # 선호하는 요일과 시간에 해당하는 경우
    for weekday in condition[member]["PreferredWeekday"]:
        if weekday in date:
            return True
        
    # 한 주에 우선순위가 높은 학생(1, 2)이 이미 포함되어 있는 경우
    if condition[member]['Priority'] == 1 or condition[member]['Priority'] == 2:
        for sol in solution:
            if condition[sol[0]]['Priority'] == 1 or condition[sol[0]]['Priority'] == 2:
                if sol[1][2] - 7 < date[2]:
                    return False
    
    # 별 조건이 없는 경우
    return True
    

def backtracking(solution, members_list, member_idx, dates_list, preempted_dates_list, condition,  N):
    if len(solution) == N:
        return solution
    
    member = members_list[member_idx]
    
    for date in dates_list:
        if is_valid(solution, member, date, condition) and not date in preempted_dates_list:
            solution.append([member, date])
            preempted_dates_list.append(date)
            
            result = backtracking(solution, members_list, member_idx + 1, dates_list, preempted_dates_list, condition, N)
            
            if result:  # 유효한 솔루션을 찾으면 바로 리턴
                return result
            
            solution.pop()
            preempted_dates_list.pop()