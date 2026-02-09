import sys
import os

path = r'c:\dev\Forkast\platform_ui\templates\platform_ui\index_v2.html'
# New Modal HTML
modal_html = """    <!-- Decision Modal -->
    <div id="decision-modal" class="fixed inset-0 z-[200] hidden items-center justify-center">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" onclick="closeDecisionModal()"></div>
        <div class="relative glass bg-gray-900 border border-gray-700 p-8 md:p-12 rounded-2xl max-w-3xl w-full mx-4 shadow-2xl transform transition-all scale-95 opacity-0 modal-content">
            <button onclick="closeDecisionModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl">&times;</button>
            <div class="flex items-center gap-4 mb-6">
                <span id="dm-icon" class="text-6xl">🤖</span>
                <div>
                    <span id="dm-category" class="text-blue-400 font-bold uppercase tracking-wider text-sm">Category</span>
                    <h3 id="dm-title" class="text-3xl font-bold mt-1">Title</h3>
                </div>
            </div>
            <div class="bg-gray-800/50 p-6 rounded-xl border border-gray-700/50 mb-8">
                <div id="dm-content" class="text-gray-300 text-lg leading-relaxed whitespace-pre-line">Content</div>
            </div>
            <div class="flex justify-end gap-4">
                <button onclick="closeDecisionModal()" class="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white font-bold transition">닫기</button>
                <button class="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-bold transition">전략 적용하기</button>
            </div>
        </div>
    </div>
"""

# New Script Logic
script_logic = """
        // --- Decision Logic ---
        let selectedDecision = null;

        function selectDecision(type) {
            selectedDecision = type;
            const decisions = ['sales', 'profit', 'customer'];
            
            decisions.forEach(d => {
                const el = document.getElementById(`decision-${d}`);
                if (d === type) {
                    el.classList.add('scale-110');
                    el.classList.remove('opacity-50');
                    el.querySelector('div').classList.add('ring-4', 'ring-white');
                } else {
                    el.classList.remove('scale-110');
                    el.classList.add('opacity-50');
                    el.querySelector('div').classList.remove('ring-4', 'ring-white');
                }
            });
        }

        function executeStrategy() {
            const btn = document.getElementById('btn-execute-strategy');
            
            if (!selectedDecision) {
                alert('먼저 성공 전략(매출, 이익, 고객) 중 하나를 선택해주세요.');
                return;
            }

            // 1. Loading State
            btn.disabled = true;
            btn.innerHTML = '<span class="animate-spin">↻</span> AI 분석 중...';
            btn.classList.add('opacity-75', 'cursor-not-allowed');

            // 2. Simulate API Call
            setTimeout(() => {
                // 3. Reset Button
                btn.disabled = false;
                btn.innerHTML = '<span>🚀</span> 전략 승인 및 실행';
                btn.classList.remove('opacity-75', 'cursor-not-allowed');

                // 4. Open Modal
                openDecisionModal(selectedDecision);

            }, 1000);
        }

        function openDecisionModal(type) {
            const modal = document.getElementById('decision-modal');
            const content = modal.querySelector('.modal-content');
            
            // Content Map
            const data = {
                'sales': {
                    icon: '💰',
                    category: 'REVENUE GROWTH',
                    title: '매출 극대화 전략',
                    content: `AI가 분석한 결과, 현재 **테이크아웃** 매출 비중이 상승하고 있습니다.\\n\\n1. **타임 세일**: 14:00~16:00 사이 테이크아웃 10% 할인을 적용하면 매출 15% 상승이 예상됩니다.\\n2. **세트 메뉴**: 인기 메뉴와 음료를 결합한 '1인 세트'를 출시하여 객단가를 높이세요.`
                },
                'profit': {
                    icon: '⚖️',
                    category: 'COST OPTIMIZATION',
                    title: '순이익 개선 전략',
                    content: `재료비 절감이 필요한 시점입니다.\\n\\n1. **재고 최적화**: '우유' 재고가 과다하므로, 라떼류 프로모션을 진행하여 소진율을 높이세요.\\n2. **로스율 관리**: 마감 1시간 전 신선 식품 30% 할인을 자동 적용하여 폐기 비용을 0원으로 만드십시오.`
                },
                'customer': {
                    icon: '💖',
                    category: 'CUSTOMER LOYALTY',
                    title: '고객 만족 & 재방문 유도',
                    content: `신규 고객 유입은 좋으나 재방문율이 5% 감소했습니다.\\n\\n1. **리뷰 이벤트**: 영수증 리뷰 작성 시 '아메리카노 쿠폰'을 증정하여 재방문 동기를 부여하세요.\\n2. **단골 케어**: 주 3회 이상 방문 고객에게 '감사 쿠키'를 증정하는 캠페인을 시작하세요.`
                }
            };

            const d = data[type];
            document.getElementById('dm-icon').innerText = d.icon;
            document.getElementById('dm-category').innerText = d.category;
            document.getElementById('dm-title').innerText = d.title;
            document.getElementById('dm-content').innerHTML = d.content;

            modal.classList.remove('hidden');
            modal.classList.add('flex');
            setTimeout(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }, 10);
            document.body.style.overflow = 'hidden';
        }

        function closeDecisionModal() {
            const modal = document.getElementById('decision-modal');
            const content = modal.querySelector('.modal-content');
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');

            setTimeout(() => {
                modal.classList.remove('flex');
                modal.classList.add('hidden');
                document.body.style.overflow = '';
            }, 300);
        }
"""

try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    function_replaced = False
    
    for line in lines:
        if 'function executeStrategy() {' in line and not function_replaced:
             # Skip old function lines until closing brace (approx)
             # Better strategy: We can't easily skip blocks in line iteration.
             # Let's append everything EXCEPT the old function, but that's hard.
             # Alternative: Just append the new modal before </body> and replace the function using string replacement.
             pass
    
    # 1. Insert Modal before </body>
    # 2. Replace old executeStrategy with new Logic block
    
    content = "".join(lines)
    
    # Insert Modal
    if '<!-- Video Modal -->' in content:
        content = content.replace('<!-- Video Modal -->', modal_html + '\n\n    <!-- Video Modal -->')
    else:
        print("Error: Video modal marker not found")
        
    # Replace Function
    # We need to find the old executeStrategy function block to replace it entirely
    # But it's easier to just assume the previous `replace_file_content` finding was correct?
    # Let's use string find/replace for the function
    
    # Old function signature start
    start_idx = content.find('function executeStrategy() {')
    
    # Find the end of that function (it has timeouts, so nested braces)
    # This is tricky with simple find.
    # Let's try to just append the new logic at the END of the script tag, and rename the old one
    # or just overwrite it.
    
    # Actually, let's just append the new script functions at the end of the <script> block
    # and rename the old executeStrategy via replacement to avoid conflict.
    
    content = content.replace('function executeStrategy() {', 'function executeStrategy_OLD() {')
    
    # Inject new logic before closing script tag
    last_script_idx = content.rfind('</script>')
    if last_script_idx != -1:
        content = content[:last_script_idx] + script_logic + content[last_script_idx:]
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Success: Modal and Logic injected")

except Exception as e:
    print(f"Error: {e}")
