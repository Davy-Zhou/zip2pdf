import os 
import sys
from time import sleep
import zipfile
from pywinauto.application import Application
from colorama import init 
from traceback import print_exc
from subprocess import run as sbp_run
from pywinauto.keyboard import send_keys
from rarfile import RarFile
# from unrar import rarfile


# ok TODO 加密压缩包解密
# ok TODO rar解密支持
# TODO 多个压缩包批量解密

def rar2pdg(filename):
    # 检查是否为rar文件,交给调用者判断吧
    with RarFile(filename) as rf:
        pwds=true_pwd=None
        path=os.path.dirname(filename)
        py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
        unrar_path=py_dirname+"\\7-Zip\\UnRAR.exe"
        rinfo=rf.infolist()
        op_path=path if (rinfo[0].filename+rinfo[1].filename).find("/")!=-1 else filename.strip(".rar")
        # TODO 爆破rar密码
        if rf.needs_password():
            pwd_path=py_dirname+"\\passwords\\passwords.txt"
            with open(pwd_path,'r',encoding='utf8') as f:
                pwds=f.readlines()
            for pwd in pwds:
                try:
                    # 测试两次，同目录原因
                    # extract_item1=rf.extract(rinfo[1],path,pwd.rstrip("\n"))
                    # extract_item2=rf.extract(rinfo[2],path,pwd.rstrip("\n"))
                    # rf.extract() BadRarFile: Failed the read enough data: req=53187 got=0 一直未解决！！！
                    # 解压目录
                    test_pwd=sbp_run([unrar_path,'x',filename,rinfo[1].filename.replace("/","\\"),rinfo[2].filename.replace("/","\\"),'-op'+op_path,'-p'+pwd.rstrip("\n"),'-y','-inul'])
                    if test_pwd.returncode==0:
                            true_pwd=pwd.rstrip("\n")
                            print(filename+" \033[0;31;40m解压密码为：\033[0m\033[0;32;40m"+true_pwd+"\033[0m\n")
                            break
                except:
                    pass
            # 未找到密码
            if not true_pwd:
                print(filename+" \033[0;31;40m解密失败,未找到密码,需要手动解压！\033[0m\n")
                rf.close()
                sys.exit(0)
        else: 
            true_pwd="-" #无密码情况
        
        # rar解压,均采用UnRar.exe
        completed = sbp_run([unrar_path,'x',filename,'-op'+op_path,'-p'+true_pwd,'-y','-inul'])
        if completed.returncode==0:
            print("\n"+filename+" \033[0;31;40m解压成功！\033[0m\n")
            # ok TODO 返回path,还得测试
            pdg_path=path+"\\"+rinfo[0].filename.split('/')[0] if (rinfo[0].filename+rinfo[1].filename).find("/")!=-1 else filename.strip(".rar")
            return pdg_path

def zip2pdg(filename):
    # 非zip压缩文件，退出
    if not zipfile.is_zipfile(filename):
        print(filename+" \033[0;31;40m非ZIP压缩包！\033[0m\n")
        sys.exit()

    with zipfile.ZipFile(filename) as zf:
        # ok TODO 压缩包加密，退出 https://stackoverflow.com/a/12038744/10628285
        zinfo=zf.infolist()
        pwds=None
        # 解释下，为什么flag_bits要测试两次？
        # 因为压缩包里面可能包含目录，但目录是不会加密的，不多加一次判断，目录里面的文件加密就发现不了
        if (zinfo[1].flag_bits & 0x1) or (zinfo[2].flag_bits & 0x1):
            print(filename+" \033[0;31;40m是加密压缩包！\033[0m\n")
            # 常用密码 https://readfree.net/bbs/forum.php?mod=viewthread&tid=5898121&extra=page%3D1
            # pwds=['52gv','28zrs']
            py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
            pwd_path=py_dirname+"\\passwords\\passwords.txt"
            with open(pwd_path,'r',encoding='utf8') as f:
                pwds=f.readlines()
            # sys.exit()

        # ok TODO 压缩文件是为目录,直接解压
        path=os.path.dirname(filename)
        if not (zinfo[0].is_dir() or len(zinfo[0].filename.split('/'))!=1):
            if not os.path.exists(filename.strip(".zip")):
                os.mkdir(filename.strip(".zip"))
            path=filename.strip(".zip")

        # ok TODO 解决解压目录中文乱码问题 https://stackoverflow.com/a/54111461/10628285
        true_pwd=None
        for member in zinfo:
            member.filename = member.filename.encode('cp437').decode('gbk')
            if pwds and (not true_pwd):
                for pwd in pwds:
                    pwd_strip=pwd.rstrip("\n")
                    try:
                        extract_item=zf.extract(member,path,pwd_strip.encode('gbk'))
                        # 目录是没有密码的
                        if os.path.isfile(extract_item):
                            true_pwd=pwd_strip
                            print(filename+" \033[0;31;40m解压密码为：\033[0m\033[0;32;40m"+true_pwd+"\033[0m\n")
                            break
                    except NotImplementedError:
                        print(filename+" \033[0;31;40m加密方式为AES-256,不支持,需要手动解压！\033[0m\n")
                        zf.close()
                        sys.exit(0)
                    except:
                        if pwd ==pwds[-1]:
                            print(filename+" \033[0;31;40m解密失败,需要手动解压！\033[0m\n")
                            zf.close()
                            sys.exit(0)
                        pass
            if not true_pwd:
                zf.extract(member,path)
        if true_pwd:
            # ok TODO 7z.exe
            zip_path=py_dirname+"\\7-Zip\\7z.exe"
            completed = sbp_run([zip_path,'x',filename,'-o'+path,'-p'+true_pwd,'-y'])
            if completed.returncode==0:
                print("\n"+filename+" \033[0;31;40m解压成功！\033[0m\n")


        # 返回pdg目录名
        return (path+"\\"+zinfo[0].filename.split('/')[0] if path==os.path.dirname(filename) else filename.strip(".zip"))


# ok TODO PDG转PDF

def pdg2pdf(dirname):
    # ok TODO file_name解析
    py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
    path = py_dirname+ "\\Pdg2Pic\\Pdg2Pic.exe"
    app = Application(backend='uia').start(path)
    # app = Application(backend='win32').start(path)
    # 连接软件的主窗口
    dlg_spec = app.window(title_re='Pdg2Pic*', class_name_re='#32770*')
    # 设置焦点，使其处于活动状态
    dlg_spec.set_focus()
    # dlg_spec.print_control_identifiers()
    # dlg_spec['Static2'].set_window_text(dirname)
    # sleep(60)
    # 选择pdg目录，
    # sleep(1.0)
    send_keys('1', 0.05, False, False,  False, True,False)
    # sleep(1.5)
    # dlg_spec['Button2'].click()

    # 选择桌面，以便确定
    dlg_spec['TreeItem'].click_input()

    # 设置pdg目录
    dlg_spec['文件夹(F):Edit'].set_edit_text(dirname)
    # sleep(0.5)
    send_keys('{ENTER}')
    # dlg_spec['确定Button'].click()
    # sleep(2)
    # dlg_spec.print_control_identifiers()
    # sleep(60)
    # Timings.slow()

    # ok_dialog = app.window(title='格式统计')
    # ok_dialog.wait("ready",5,0.5)
    # ok_dialog.print_control_identifiers()
    # ok_dialog['OKButton'].click_input()
    prepared_time=len(os.listdir(dirname))/250
    sleep(1+prepared_time)
#    sleep(60)
    # dlg_spec.set_focus()
    send_keys('{ENTER}')
    # dlg_spec['OKButton'].wait("ready",60,1)
    # dlg_spec['OKButton'].click_input()
    # ok TODO 转换性能问题,sleep时间还是要根据页数动态调整下才行
    # dlg_spec['4、开始转换Button'].click()
    sleep(0.5)
    send_keys('{ENTER}')
    # send_keys('4', 0.05, False, False,  False, True,False)
    # ok TODO 转换需要时间，怎么判断？
    # send_keys('%{ESC}')
    # complete_dialog = dlg_spec.child_window(title='Pdg2Pic')
    # complete_dialog.wait("exists",80,1)
    # ok TODO 明天做，有个新思路，改为监控输出，PDF大小不再变化即为完成 https://stackoverflow.com/a/37256114/10628285
    sleep(2)
    pdf_name = dirname+".pdf"
    if os.path.exists(pdf_name):
        while True:
            try:
                os.rename(pdf_name, pdf_name)
                sleep(1)
                send_keys('%{F4}' '%{F4}')
                break
            except OSError as e:
                sleep(1)

    # dlg_spec.wait("visible",30,1)
    # sleep(1.5)
    # send_keys('%{F4}' '%{F4}')
    # send_keys('{ENTER}')

    # while dlg_spec['Static23'].window_text()[:5]=='存盘...':
        # sleep(1.5)
        # send_keys('{ENTER}')
        # dlg_spec.close()
        # break
    
    # 转换完毕
#    dlg_spec['OKButton'].wait("ready",10,1)
    # dlg_spec['OKButton'].click_input()

    return dlg_spec
    # 测试
    # dlg_spec.close()    
    # send_keys('4')
    # dlg_spec.print_control_identifiers()
    # print(dlg_spec['Static23'].window_text()[:5]+'\n')



if __name__ == '__main__':
    os.system("title " + "zip2pdf@DavyZhou v0.20 2022-12-8")
    print("软件更新请访问："+"\033[0;32;40m https://github.com/Davy-Zhou/zip2pdf \033[0m"+"\n")
    print("暂时只支持zip、rar和已解压pdg目录，\033[0;32;40m直接拖入需要合并成PDF的zip、rar压缩包或已解压pdg目录即可\033[0m\n")
    if len(sys.argv) == 2:
        filename=sys.argv[1]
    elif len(sys.argv) == 1:
        filename=input("请输入zip、rar文件或pdg目录：").replace("\"","").rstrip(' ')
    i=0
    init()
    while True:
        try:
            if os.path.isfile(filename):
                # ok TODO 压缩包类型判断
                print("\n正在测试解压密码， \033[0;31;40m请等待...\033[0m\n")
                if filename.lower().endswith('.zip'):
                    dirname=zip2pdg(filename)
                elif filename.lower().endswith('.rar'):
                    dirname=rar2pdg(filename)
                # input()
                print("\n\n"+filename+" \033[0;32;40m已解压成PDG!\033[0m")
            else:
                dirname=filename
            dlg_spec=pdg2pdf(dirname)
            # 关闭PDG2Pic
            # sleep(1)
            # dlg_spec['Close2'].click()
            print("\n\n"+filename+" \033[0;32;40m已转成PDF!\033[0m\n\n")
        except:
            print('\n')
            print_exc()
            print("\n\033[0;32;40m程序运行有问题，记录出错信息，按enter键退出\033[0m\n")
        i=i+1
        print("\033[0;31;40m重开+"+str(i)+"\033[0m\n")
        dirname=filename=None
        # 重复Input,cmd会自动加空格，然后出现莫名Bug
        filename=input("请输入zip、rar文件或pdg目录：").replace("\"","").rstrip(' ')











