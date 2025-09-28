document.addEventListener('DOMContentLoaded', function() {
            // --------------------------
            // 功能一：夜间模式切换
            // --------------------------
            const darkModeButton = document.getElementById('toggle-dark-mode');
            const bodyElement = document.body;
            console.log('夜间模式按钮是否存在：', darkModeButton ? '是' : '否');
            
            if (darkModeButton) {
                darkModeButton.addEventListener('click', function() {
                    bodyElement.classList.toggle('dark-mode');
                    console.log('夜间模式切换，当前状态：', bodyElement.classList.contains('dark-mode'));
                });
            }

            // --------------------------
            // 功能二：添加项目经历
            // --------------------------
            const addProjectBtn = document.getElementById('add-project-btn');
            const newProjectInput = document.getElementById('new-project-input');
            const projectList = document.getElementById('project-list');
            console.log('添加项目按钮是否存在：', addProjectBtn ? '是' : '否');
            console.log('项目列表是否存在：', projectList ? '是' : '否');
            
            if (addProjectBtn && newProjectInput && projectList) {
                addProjectBtn.addEventListener('click', function() {
                    const newProjectText = newProjectInput.value.trim();
                    
                    if (!newProjectText) {
                        alert('请输入项目名称！');
                        return;
                    }
                    
                    const newListItem = document.createElement('li');
                    newListItem.className = 'list-group-item';
                    newListItem.textContent = newProjectText;
                    projectList.appendChild(newListItem);
                    newProjectInput.value = '';
                    console.log('添加项目成功：', newProjectText);
                });
            }

            // --------------------------
            // jQuery功能
            // --------------------------
            $(document).ready(function() {
                // 功能三：点击技能项隐藏
                $('#skills-list li').on('click', function() {
                    $(this).fadeOut('slow');
                });

                // 功能四：点击个人简介标题展开/收起
                const bioTitle = $('#main-title').next('.section-title');
                bioTitle.css('cursor', 'pointer');
                bioTitle.on('click', function() {
                    $(this).nextAll('h3, h4, h5').slideToggle('slow');
                });
            });
        });