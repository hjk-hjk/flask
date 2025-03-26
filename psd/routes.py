import os.path
from fileinput import filename

from flask import Flask, render_template
from flask import request, redirect, url_for
import cx_Oracle
file_dir = 'static/psd/files/'

from  .  import psd_bp

# 오라클 DB 연동하기
def  get_db_connection():
    dsn = cx_Oracle.makedsn('localhost','1521', service_name='XE')
    connection = cx_Oracle.connect(user='majustory',password='1234', dsn=dsn)
    return connection

@psd_bp.route('/psd_list')
def  psd_list():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("select idx, sname, title, content, files,cnt  from  psd order  by  idx  desc")

    column_names = [desc[0].lower() for desc in cursor.description]

    '''
    column_names = []
    for desc in cursor.description:
        column_names.append(desc[0].lower())
    '''

    rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    '''
    rows = []
    for row in cursor.fetchall():
        rows.append(dict(zip(column_names, row)))
    '''
    cursor.close()
    connection.close()
    return render_template('psd/list.html', rows=rows)

@psd_bp.route('/psd_form')
def  psd_form():
    return  render_template('psd/form.html')

@psd_bp.route('/psd_save', methods=['post'])
def psd_save():
    from datetime import datetime
    file_dir = 'static/psd/files/'
# 파일 먼저 처리해야 함
    file = request.files['file']
    file_path = os.path.join(file_dir, file.filename)
    if os.path.exists(file_path):
        name, ext = os.path.splitext(file.filename)
# 시분초 출력
        timestr = datetime.now().strftime("%H%M%S")
        filename = f"{name}_{timestr}.{ext}"
        file_path = os.path.join(file_dir, filename)
        file.save(file_path)
    else:
        filename=file.filename
        file.save(file_path)

    sname = request.form['sname']
    title = request.form['title']
    content = request.form['content']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
      '''
         insert into psd(idx, sname, title, content,files,cnt)
         values(idx_psd.nextval, :1, :2,:3,:4, 0)
      ''',(sname, title,content,filename)
    )
    
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('psd_bp.psd_list'))

@psd_bp.route('/psd_delete')
def  psd_delete():
    # GET 방법으로 값 받아오기
    idx = request.args.get("idx")
    files = request.args.get("files")
    del_file = file_dir + files
    if os.path.exists(del_file):
        os.remove(del_file)

    print("====> psd_delete",idx,files)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
                   delete from psd where idx = :1
                   """
                   , (idx,))

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('psd_bp.psd_list'))

@psd_bp.route('/psd_edit')
def  psd_edit():
    # GET 방법으로 값 받아오기
    idx = request.args.get("idx")

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        '''
           update psd 
           set cnt = cnt + 1
           where idx=:1          
        ''', (idx,)
    )
    connection.commit()

    cursor.execute("""
                   select * from psd where idx = :1
                   """
                   , (idx,))
    row = cursor.fetchone()
    #튜플 값을 딕셔너리로 변경해서 컬럼이름을 사용할 수 있게 함
    if row :
        column_names = [desc[0].lower() for desc in cursor.description]
        result = dict(zip(column_names, row))

        return  render_template('psd/edit.html' , row= result )

    cursor.close()
    connection.close()

@psd_bp.route('/psd_update', methods=['post'])
def psd_update():
    connection = get_db_connection()
    cursor = connection.cursor()

    idx = request.form['idx']
    sname = request.form['sname']
    title = request.form['title']
    content = request.form['content']
    files = request.files['files']

    if files.filename != "":
        cursor.execute("""
                         select * from psd where idx = :1
                         """
                       , (idx,))
        row = cursor.fetchone()
        result = ""
        if row:
            column_names = [desc[0].lower() for desc in cursor.description]
            result = dict(zip(column_names, row))

        del_file = file_dir + result['files']
        if os.path.exists(del_file):
            print("===>수정 del_file : ", del_file)
            os.remove(del_file)

        file_path = os.path.join(file_dir, files.filename)
        filename = ""
        if os.path.exists(file_path):
            name, ext = os.path.splitext(files.filename)
            from datetime import datetime
            timestr = datetime.now().strftime("%H%M%S")
            filename = f"{name}_{timestr}{ext}"
            file_path = os.path.join(file_dir, filename)
            files.save(file_path)

        else:
            filename = files.filename
            files.save(file_path)

        cursor.execute(
            '''
               update psd 
               set sname =:1, title =:2, content=:3 , files = :4
               where idx=:5          
            ''', (sname, title, content, filename, idx)
        )
        connection.commit()
    else:
        cursor.execute(
            '''
               update psd 
               set sname =:1, title =:2, content=:3 
               where idx=:4          
            ''', (sname, title, content, idx)
        )
        connection.commit()

    cursor.close()
    connection.close()
    return redirect(url_for('psd_bp.psd_list'))


@psd_bp.route('/psd_insert')
def psd_insert():
    from faker import Faker
    fake = Faker('ko-KR')

    connection = get_db_connection()
    cursor = connection.cursor()
    for i in range(100):
        sname = fake.name()
        title = fake.company()
        content = fake.text()

        cursor.execute(
          '''
             insert into psd(idx, sname, title, content,cnt)
             values(idx_psd.nextval, :1, :2,:3,:4, 0)
          ''',(sname, title,content)
        )
        connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('psd_bp.psd_list'))
