import os 
import sys
from time import sleep
import zipfile
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from colorama import init 
from traceback import print_exc
from subprocess import run as sbp_run
from rarfile import RarFile
from pyzipper import AESZipFile
from configparser import ConfigParser


# ok TODO 加密压缩包解密
# ok TODO rar解密支持
# TODO 多个压缩包批量解密

# rar解压
def rar2pdg(filename):
    # 检查是否为rar文件,交给调用者判断吧
    with RarFile(filename) as rf:
        pwds=true_pwd=None
        path=os.path.dirname(filename)
        py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
        unrar_path=py_dirname+"\\7-Zip\\UnRAR.exe"
        # 解压目录
        rinfo=rf.infolist()
        op_path=path if len(rinfo) > 1 and (rinfo[0].filename+rinfo[1].filename).find("/")!=-1 else filename.strip(".rar")
        # op_path=r"D:\Users\Acer\Documents\du xiu\dx_book"
        # ok TODO 爆破rar密码
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
                    if len(rinfo)==1:
                        test_pwd=sbp_run([unrar_path,'x',filename,rinfo[0].filename.replace("/","\\"),'-op'+op_path,'-p'+pwd.rstrip("\n"),'-y','-inul'])
                    elif len(rinfo)>1:
                        test_pwd=sbp_run([unrar_path,'x',filename,rinfo[0].filename.replace("/","\\"),rinfo[1].filename.replace("/","\\"),'-op'+op_path,'-p'+pwd.rstrip("\n"),'-y','-inul'])
                    elif len(rinfo)==0:
                        test_pwd=sbp_run([unrar_path,'x',filename,'-op'+op_path,'-p'+pwd.rstrip("\n"),'-y','-inul'])
                        # pdg_path=os.path.splitext(filename)[0]
                    if test_pwd.returncode==0:
                            true_pwd=pwd.rstrip("\n")
                            print(filename+" \033[0;31;40m解压密码为：\033[0m\033[0;32;40m"+true_pwd+"\033[0m\n")
                            break
                except:
                    pass
            # 未找到密码
            if not true_pwd :
                print(filename+" \033[0;31;40m解密失败,未找到密码,需要手动解压！\033[0m\n")
                rf.close()
                sys.exit(0)
        else: 
            true_pwd="-" #无密码情况
        
        # rar解压,均采用UnRar.exe
        if len(rinfo)>0:
            completed = sbp_run([unrar_path,'x',filename,'-op'+op_path,'-p'+true_pwd,'-y','-inul'])
            if completed.returncode==0:
                print("\n"+filename+" \033[0;31;40m解压成功！\033[0m\n")
                # ok TODO 返回path,还得测试
        pdg_path=path+"\\"+rinfo[0].filename.split('/')[0] if len(rinfo)>1 and (rinfo[0].filename+rinfo[1].filename).find("/")!=-1 else os.path.splitext(filename)[0]
        return pdg_path

# AES ZIP解压
def aeszip2pdg(filename,pwds):
    path=filename.rstrip("."+filename.split(".")[-1])
    with AESZipFile(filename) as af:
        ainfo=af.infolist()
        for pwd in pwds:
            pwd_strip=pwd.rstrip("\n")
            try:
                extract_item1=af.extract(ainfo[0],path,pwd_strip.encode('gbk'))
                if len(ainfo) > 1:
                    extract_item2=af.extract(ainfo[1],path,pwd_strip.encode('gbk'))
                if os.path.isfile(extract_item1) or (len(ainfo) > 1 and os.path.isfile(extract_item2)):
                    true_pwd=pwd_strip
                    print(filename+" \033[0;31;40m解压密码为：\033[0m\033[0;32;40m"+true_pwd+"\033[0m\n")
                    break
            except:
                if pwd ==pwds[-1]:
                    print(filename+" \033[0;31;40m解密失败,没找到密码,需要手动解压！\033[0m\n")
                    af.close()
                    sys.exit(0)
                pass
    return true_pwd
# 普通加密ZIP解压
def zip2pdg(filename):
    # 非zip压缩文件，退出
    if not zipfile.is_zipfile(filename):
        print(filename+" \033[0;31;40m非ZIP压缩包！\033[0m\n")
        sys.exit()

    with zipfile.ZipFile(filename) as zf:
        # ok TODO 压缩包加密，退出 https://stackoverflow.com/a/12038744/10628285
        zinfo=zf.infolist()
        pwds=None
        py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
        # 解释下，为什么flag_bits要测试两次？
        # 因为压缩包里面可能包含目录，但目录是不会加密的，不多加一次判断，目录里面的文件加密就发现不了
        if (zinfo[0].flag_bits & 0x1) or (len(zinfo) > 1 and zinfo[1].flag_bits & 0x1):
            print(filename+" \033[0;31;40m是加密压缩包！\033[0m\n")
            # 常用密码 https://readfree.net/bbs/forum.php?mod=viewthread&tid=5898121&extra=page%3D1
            # pwds=['52gv','28zrs']
            pwd_path=py_dirname+"\\passwords\\passwords.txt"
            with open(pwd_path,'r',encoding='utf8') as f:
                pwds=f.readlines()
            # sys.exit()

        #  TODO 压缩文件是为目录,直接解压,考虑无后缀情形以及多后缀情形
        path=filename.rstrip("."+filename.split(".")[-1])
        # if not (zinfo[0].is_dir() or len(zinfo[0].filename.split('/'))!=1):
            # if not os.path.exists(filename.strip(".zip")):
                # os.mkdir(filename.strip(".zip"))
            # path=filename.strip(".zip")

        # ok TODO 解决解压目录中文乱码问题 https://stackoverflow.com/a/54111461/10628285
        true_pwd=None
        for member in zinfo:
            # member.filename = member.filename.encode('cp437').decode('gb18030')
#            bug 记得修
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
                        print(filename+" \033[0;31;40m加密方式为AES-256\033[0m\n")
                        # ok TODO AES解密支持
                        zf.close()
                        true_pwd=aeszip2pdg(filename,pwds)
                        break
                    except:
                        if pwd ==pwds[-1]:
                            print(filename+" \033[0;31;40m解密失败,没找到密码,需要手动解压！\033[0m\n")
                            zf.close()
                            sys.exit(0)
                        pass
            # if not true_pwd:
                # zf.extract(member,path)
        if not true_pwd:
            true_pwd="-"
        # ok TODO 7z.exe
        zip_path=py_dirname+"\\7-Zip\\7z.exe"
        completed = sbp_run([zip_path,'e',filename,'-o'+path,'-p'+true_pwd,'-y'])
        if completed.returncode==0:
            print("\n"+filename+" \033[0;31;40m解压成功！\033[0m\n")


        # 返回pdg目录名
        return path

# 判断PDG目录内是否为PDG文件及处理
def is_pdg(dirname):
    file_list=os.listdir(dirname)
    # pdf_flag用于标识dirname内是否有pdf文件
    pdf_flag = False
    for f in file_list:
        abs_path=os.path.join(dirname,f)
        # 压缩包为文件
        if os.path.isfile(abs_path):
            # 图片重命名
            if f.lower().endswith(('.jpg','.png','bmp','.tiff','gif','webp','.tif')):
                pdg_suffix_path=os.path.join(dirname,os.path.splitext(f)[0]+'.pdg')
                os.rename(abs_path,pdg_suffix_path)
            # pdf移动到上级目录
            elif f.lower().endswith(('.pdf','.djvu')):
                pdf_flag=True
                parent_path=os.path.join(os.path.split(dirname)[0],f)
                os.rename(abs_path,parent_path)
        # 压缩包内是目录，移动到上级目录，并再检查目录文件
        elif len(file_list)==1 and os.path.isdir(abs_path):
            parent_path=os.path.join(os.path.split(dirname)[0],f)
            os.rename(abs_path,parent_path)
            os.rmdir(dirname)
            pdf_flag,dirname=is_pdg(parent_path)

    return pdf_flag,dirname


# ok TODO PDG转PDF

def pdg2pdf(dirname,use_virtual_machine):
    # ok TODO file_name解析
    py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
    path = py_dirname+ "\\Pdg2Pic\\Pdg2Pic.exe"
    app = Application(backend='uia').start(path)
    # 连接软件的主窗口
    dlg_spec = app.window(title_re='Pdg2Pic*', class_name_re='#32770*')

    # 设置焦点，使其处于活动状态
    dlg_spec.set_focus()

    # 选择pdg目录，
    send_keys('1', 0.05, False, False,  False, True,False)

    # 选择桌面，以便确定,针对MAC下虚拟机使用windows优化
    if use_virtual_machine:
        j=2
        try:
            dlg_spec['TreeItem'+str(j)].click_input()
            dlg_spec['文件夹(F):Edit'].set_edit_text(dirname)
        except:
            # 考虑到性能，还是用tree_item_count
            tree_item_count=len(dlg_spec['TreeItem1'].wrapper_object().sub_elements())
            while j<=tree_item_count+1:
                j+=1
                dlg_spec['TreeItem'+str(j)].click_input()
                # 考虑报错
                if dlg_spec['确定Button'].wrapper_object().parent().window_text()!='选择存放PDG文件的文件夹':
                    dlg_spec['确定Button'].click_input()
                # 确定Button能点击了
                if dlg_spec['确定Button'].wrapper_object().is_enabled():
                    dlg_spec['文件夹(F):Edit'].set_edit_text(dirname)
                    break
    # 真机
    else:
        try:
            dlg_spec['TreeItem1'].click_input()
            # 设置pdg目录
            dlg_spec['文件夹(F):Edit'].set_edit_text(dirname)
        except:
            print("\n无法点击确定按钮，\033[0;31;40m请在配置文件 (zip2pdf\Config\config.ini) 中设置"+"\033[0;32;40m use_virtual_machine \033[0m"+"选项为\033[0m"+"\033[0;32;40m ture \033[0m，或需要手动拖入PDG目录转换！\n")
            sys.exit(0)

    send_keys('{ENTER}')

    # ok_dialog = app.window(title='格式统计')
    # ok_dialog.wait("ready",5,0.5)
    # ok_dialog.print_control_identifiers()
    # ok_dialog['OKButton'].click_input()
    prepared_time=len(os.listdir(dirname))/250
    sleep(1+prepared_time)

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
                sleep(0.5)
                # send_keys('%{F4}' '%{F4}')
                app.kill()
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

#    return dlg_spec

if __name__ == '__main__':
    os.system("title " + "zip2pdf@DavyZhou v0.40 2023-1-7")
    print("软件更新请访问："+"\033[0;32;40m https://github.com/Davy-Zhou/zip2pdf \033[0m"+"\n")
    print("暂时只支持zip、rar、cbz、uvz和已解压pdg目录，\033[0;32;40m直接拖入需要合并成PDF的zip、rar、cbz、uvz压缩包或已解压pdg目录即可\033[0m\n")
    print("\033[0;30;41m警告：\033[0m"+"\033[0;32;40m本程序在使用过程中会占用鼠标和键盘，未运行完成，请不要使用鼠标和键盘！\033[0m\n")
    if len(sys.argv) == 2:
        filename=sys.argv[1]
    elif len(sys.argv) == 1:
        filename=input("请输入zip、rar、cbz、uvz文件或pdg目录：").replace("\"","").rstrip(' ')
    i=0
    init()
    py_dirname= os.path.dirname(os.path.abspath(sys.argv[0]))
    while True:
        parser = ConfigParser()
        parser.read(py_dirname+'\\Config\\config.ini',"utf-8")
        use_virtual_machine=parser.getboolean('General','use_virtual_machine')
        del_compressed_package=parser.getboolean('General','del_compressed_package')
        del_decompression_dir=parser.getboolean('General','del_decompression_dir')

        # TODO 选中多个压缩包转PDF
            # while 
            
        # TODO 选中包含压缩包的目录转PDF
        try:
            if os.path.isfile(filename):
                # ok TODO 压缩包类型判断,增加UVZ、cbz格式
                print("\n正在测试解压密码， \033[0;31;40m请等待...\033[0m\n")
                if filename.lower().endswith(('.zip','.uvz','.cbz')):
                    dirname=zip2pdg(filename)
                elif filename.lower().endswith('.rar'):
                    dirname=rar2pdg(filename)
                # input()
                print("\n\n"+filename+" \033[0;32;40m已解压成PDG!\033[0m")
#                删除压缩包
                if del_compressed_package:
                    os.remove(filename)
            else:
                dirname=filename
            # dirname包含pdg,才转换
            pdf_flag,dirname=is_pdg(dirname)
            if not pdf_flag:
                pdg2pdf(dirname,use_virtual_machine)
#            递归删除解压目录 https://www.cnblogs.com/Raul2018/p/11640485.html
            if del_decompression_dir:
                for root, dirs, files in os.walk(dirname, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(dirname)

            print("\n\n"+filename+" \033[0;32;40m已转成PDF!\033[0m\n\n")
        except:
            print('\n')
            print_exc()
            print("\n\033[0;32;40m程序运行有问题，记录出错信息\033[0m\n")
            # print("\n\033[0;31;40m发报错截图,在Github提Issue,或者在群里\033[0m"+" \033[0;32;40m@just\033[0m\n")
            # print("\n\033[0;32;40m提Issue: https://github.com/Davy-Zhou/zip2pdf/issues \033[0m\n")
        i=i+1
        print("\033[0;31;40m重开 +"+str(i)+"\033[0m\n")
        print("\033[0;30;41m警告：\033[0m"+"\033[0;32;40m本程序在使用过程中会占用鼠标和键盘，未运行完成，请不要使用鼠标和键盘！\033[0m\n")
        dirname=filename=None
        # 重复Input,cmd会自动加空格，然后出现莫名Bug
        filename=input("请输入zip、rar、cbz、uvz文件或pdg目录：").replace("\"","").rstrip(' ')











