#include <linux/module.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/moduleparam.h>
#include <linux/mm.h>
#include <linux/sched.h>
#include <linux/string.h>
#include <linux/fs.h>
#include <asm/pgtable.h>
#include <asm/unistd.h>
#include <asm/uaccess.h>

#define PGD_PUD_PMD_NONE -3
#define NOT_MAPPED -2
#define NOT_IN_RAM -1
#define FILE_NAME_LEN 50
#define BUF_LEN 100

static int pid_from_user = 0;
static char *log_file = "/home/qemu/my_kernel_log_test"; // 默认路径
static int get_walk_page_status = 0;
static struct file *log_file_struct = NULL;
static mm_segment_t old_fs;
unsigned long my_find_phyaddr(struct mm_struct *my_mm, unsigned long my_va, int *status);
static int log_to_file(struct file *my_file, char *buf, unsigned int buf_len);

module_param(pid_from_user, int, 0);
module_param(log_file, charp, 0);


static int __init test_init(void){
    printk("Hello world!\n");
    int status = 0;
    unsigned int i = 0;
    struct mm_struct *my_mm = NULL;
    struct vm_area_struct *my_vm_area = NULL, *tmp = NULL;
    unsigned long my_start, my_end, my_phy_addr;
    char my_buf[BUF_LEN];

    log_file_struct = filp_open(log_file, O_RDWR | O_APPEND | O_CREAT, 0644);
    if (IS_ERR(log_file_struct)){
      printk("error occured while opening file %s\n", log_file);
      return 0;
    }
    old_fs = get_fs();
    set_fs(KERNEL_DS);

    struct task_struct *tsk = pid_task(find_vpid(pid_from_user), PIDTYPE_PID);
    if (NULL == tsk){
        printk("find pid %d failed!\n", pid_from_user);
        return 0;
    }
    my_mm = tsk->mm;
    if (NULL == my_mm){
        printk("the task %d is a kernel thread, goodbye!\n", pid_from_user);
        return 0;
    }

    my_vm_area = my_mm->mmap;
    if (NULL == my_vm_area){
        printk("there's no linear area in the task %d, goodbye!\n", pid_from_user);
        return 0;
    }
    #if 0
        printk("Basic information:");
        printk("total_vm = 0x%p, locked_vm = 0x%p, shared_vm = 0x%p, exec_vm = 0x%p\n", my_mm->total_vm, my_mm->locked_vm, my_mm->shared_vm, my_mm->exec_vm);
        printk("stack_vm = 0x%p, reserved_vm = 0x%p, def_flags = 0x%p, nr_ptes = 0x%p\n", my_mm->stack_vm, my_mm->reserved_vm, my_mm->def_flags, my_mm->nr_ptes);
        printk("start_code = 0x%p, end_code = 0x%p, start_data = 0x%p, end_data = 0x%p\n", my_mm->start_code, my_mm->end_code, my_mm->start_data, my_mm->end_data);
        printk("start_brk = 0x%p, brk = 0x%p, start_stack = 0x%p\n", my_mm->start_brk, my_mm->brk, my_mm->start_stack);
        printk("arg_start = 0x%p, arg_end = 0x%p, env_start = 0x%p, env_end = 0x%p\n", my_mm->arg_start, my_mm->arg_end, my_mm->env_start, my_mm->env_end);
    #else
       memset(my_buf, 0, sizeof(my_buf));
    #endif
    tmp = my_vm_area;
    while (tmp != NULL) {
    // printk("%d: vm_start = 0x%x, vm_end = 0x%x\n", ++i, tmp->vm_start, tmp->vm_end);
        my_start = tmp->vm_start;
        my_end = tmp->vm_end;
        while (my_end >= my_start) {
            my_phy_addr = my_find_phyaddr(my_mm, my_start, &status);
            if (PGD_PUD_PMD_NONE == status) {

            }
            else if (NOT_MAPPED == status) {

            }
            else if (NOT_IN_RAM == status) {

            }
            else {
                sprintf(my_buf, "%lx\n", my_phy_addr);
                log_to_file(log_file_struct, my_buf, BUF_LEN-1);
            }
            my_start += PAGE_SIZE;
        }
        tmp = tmp->vm_next;
    }
    return 0;
}

static void __exit test_exit(void)
{
    set_fs(old_fs);
    if (NULL != log_file_struct) {
        filp_close(log_file_struct, NULL);
    }
    printk("Goodbye the world!\n");
    return;
}

unsigned long my_find_phyaddr(struct mm_struct *my_mm, unsigned long my_va, int *status)
{
    pgd_t *pgd = NULL;
    pud_t *pud = NULL;
    pmd_t *pmd = NULL;
    pte_t *pte = NULL;

    pgd = pgd_offset(my_mm, my_va); /*get the pdg entry pointer*/
    if (pgd_none(*pgd)) {
        printk("this is impossible on ia32, maybe something is wrong, maybe I'm wrong..., line %d\n", __LINE__);
        *status = PGD_PUD_PMD_NONE;
        return 0;
    }

    pud = pud_offset(pgd, my_va);
    if (pud_none(*pud)) {
        printk("this is impossible on ia32, maybe something is wrong, maybe I'm wrong..., line %d\n", __LINE__);
        *status = PGD_PUD_PMD_NONE;
        return 0;
    }

    pmd = pmd_offset(pud, my_va);
    if (pmd_none(*pmd)) {
        printk("this is impossible on ia32, maybe something is wrong, maybe I'm wrong..., line %d\n", __LINE__);
        *status = PGD_PUD_PMD_NONE;
        return 0;
    }

    pte = pte_offset_kernel(pmd, my_va);
    if (pte_none(*pte)) {
        *status = NOT_MAPPED;
        return 0;
    }
    if (!pte_present(*pte)) {
        *status = NOT_IN_RAM;
        return 0;
    }
    *status = 0;
    return pte_val(*pte);
}

static int log_to_file(struct file *my_file, char *buf, unsigned int buf_len) {
    my_file->f_op->write(my_file, buf, strlen(buf), &my_file->f_pos);
    return 0;
}

module_init(test_init);
module_exit(test_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("地址转换");
