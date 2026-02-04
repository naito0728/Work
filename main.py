import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0728",
        database="task"
    )

#ステータスリスト
STATUS_LIST = {
    "1": "未着手",
    "2": "進行中",
    "3": "完了",
    "4": "すべて"
}

# コマンド一覧
def show_menu():
    print("\n操作を選んでください")
    print("1. タスク一覧表示")
    print("2. タスク作成")
    print("3. タスク変更")
    print("4. タスク削除")
    print("5. 終了")

# 日付形式チェック
def input_deadline():
    while True:
        deadline = input("期限(YYYY-MM-DD): ")
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
            return deadline
        except ValueError:
            print("日付入力が正しくありません。")

# ステータスは揃えたいので選択式
def select_status(allow_all=False):
    print("ステータスを選択してください")
    for k, v in STATUS_LIST.items():
        if k == "4" and not allow_all:
            continue
        print(f"{k}. {v}")

    while True:
        choice = input("番号: ")
        # ステータス：全件取得
        if choice == "4" and allow_all:
            return None
        # タスク追加時のみ全件取得用のNo.4の選択項目を除く
        if choice in STATUS_LIST and choice != "4":
            return STATUS_LIST[choice]
        
        print("無効な番号です。")

# タスク一覧表示
def task_list():
    status = select_status(allow_all = True)
    try:
        conn = get_connection()
        cur = conn.cursor()
        #ステータスで絞込
        if status:
            cur.execute("SELECT * FROM tasks WHERE status=%s", (status,))
        # 絞込がなければ全件検索
        else:
            cur.execute("SELECT * FROM tasks")

        rows = cur.fetchall()

        # データ件数無しはメッセージ出力
        if len(rows) == 0:
            print("該当するタスクがありません。")
            return

        # データがある場合は一覧表示
        for row in rows:
            print(row)

    except mysql.connector.Error as e:
        print("タスク一覧の取得中にデータベースエラーが発生しました。")
        print(e)

    except Exception as e:
        print("タスク一覧の取得中にエラーが発生しました。")
        print(e)
    
    finally:
        if conn.is_connected():
            conn.close()

# タスク追加
def task_add():
    title = input("タスク名: ")
    content = input("内容: ")
    assignee = input("担当者: ")
    deadline = input_deadline()
    status = select_status()

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, content, assignee, deadline, status) VALUES (%s,%s,%s,%s,%s)",
            (title, content, assignee, deadline, status)
        )
        conn.commit()
        conn.close()
        print("新規タスクの作成を行いました。")
    except Exception as e:
        print("タスクの作成でエラーが発生しました。")
        print(e)

# タスク変更
def task_update():
    try:
        # タスクの一覧を取得
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
        if len(rows) == 0:
            print("タスクが登録されていません。")
            return
        for row in rows:
            print(row)
    except mysql.connector.Error as e:
        print("タスクの表示中にデータベースエラーが発生しました。")
        print(e)

    finally:
        if conn.is_connected():
            conn.close()

    task_id = input("変更するタスクID: ")
    title = input("タスク名: ")
    content = input("新しい内容: ")
    deadline = input_deadline()
    status = select_status()

    # タスクの更新
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET title=%s, content=%s, deadline=%s, status=%s WHERE id=%s",
            (title, content, deadline, status, task_id)
        )

        # タスク有無で更新 or メッセージ表示
        if cur.rowcount == 0:
            print("指定されたIDのタスクは存在しません。")
        else:
            conn.commit()
            print("タスクを更新しました。")
        
        conn.commit()
    except mysql.connector.Error as e:
        print("タスク更新中にデータベースエラーが発生しました。")
        print(e)

    finally:
        if conn.is_connected():
            conn.close()

# タスク削除
def task_delete():
    try:
        # タスクの一覧を取得
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
        if len(rows) == 0:
            print("タスクが登録されていません。")
            return
        for row in rows:
            print(row)
    except mysql.connector.Error as e:
        print("タスクの表示中にデータベースエラーが発生しました。")
        print(e)

    finally:
        if conn.is_connected():
            conn.close()

    task_id = input("削除するタスクID: ")

    # 指定されたIDで削除 or エラーメッセージ表示
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))

        if cur.rowcount == 0:
            print("指定されたIDのタスクは存在しません。")
        else:
            conn.commit()
            print("タスクを削除しました。")

    except mysql.connector.Error as e:
        print("タスク削除中にデータベースエラーが発生しました。")
        print(e)

    finally:
        if conn.is_connected():
            conn.close()

# メイン処理
# 指定コマンドごとの操作
def main():
    while True:
            show_menu()
            select = input("番号を入力してください: ")

            if select == "1":
                task_list()
            elif select == "2":
                task_add()
            elif select == "3":
                task_update()
            elif select == "4":
                task_delete()
            elif select == "5":
                print("アプリを終了します。")
                break
            else:
                print("無効な番号です。")

if __name__ == "__main__":
    main()