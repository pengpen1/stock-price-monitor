<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="max-w-6xl mx-auto">
      <!-- 头部区域 -->
      <div class="flex justify-between items-center mb-5">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20"
          >
            <img src="../assets/stock.png" class="opacity-90" alt="stock" />
          </div>
          <h1
            class="text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent"
          >
            {{ $t("dashboard.title") }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <!-- <button
            @click="toggleLanguage"
            class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            {{ locale === "en" ? "中文" : "English" }}
          </button> -->
          <button
            @click="$emit('openJournal')"
            class="px-3 py-2.5 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl hover:shadow-sm transition-all duration-200 cursor-pointer"
            title="交易日志"
          >
            📝
          </button>
          <button
            @click="showUserGuide = true"
            class="px-3 py-2.5 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl hover:shadow-sm transition-all duration-200 cursor-pointer"
            title="使用手册"
          >
            📖
          </button>
          <button
            @click="showChangelog = true"
            class="px-3 py-2.5 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl hover:shadow-sm transition-all duration-200 cursor-pointer"
            title="更新日志"
          >
            📋
          </button>
          <button
            @click="$emit('openSettings')"
            class="px-3 py-2.5 text-sm text-slate-600 bg-white border border-slate-200 rounded-xl hover:shadow-sm transition-all duration-200 cursor-pointer"
          >
            ⚙️
          </button>
        </div>
      </div>

      <!-- 大盘指数 -->
      <div class="grid grid-cols-4 gap-3 mb-4">
        <div
          v-for="idx in indexList"
          :key="idx.code"
          class="group relative bg-white rounded-xl p-4 shadow-sm border border-slate-100 cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
          @click="openIndexDetail(idx.code)"
        >
          <!-- 背景装饰 -->
          <div
            class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            :class="
              parseFloat(idx.change_percent) >= 0
                ? 'bg-gradient-to-br from-red-50/50 to-transparent'
                : 'bg-gradient-to-br from-green-50/50 to-transparent'
            "
          ></div>
          <!-- 左侧装饰条 -->
          <div
            class="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
            :class="
              parseFloat(idx.change_percent) >= 0
                ? 'bg-gradient-to-b from-red-400 to-red-500'
                : 'bg-gradient-to-b from-green-400 to-green-500'
            "
          ></div>
          <div class="relative">
            <div class="text-xs text-slate-500 mb-1.5 font-medium">
              {{ idx.name }}
            </div>
            <div class="flex items-baseline gap-2">
              <span
                class="text-xl font-bold tracking-tight"
                :class="getIndexClass(idx.change_percent)"
                >{{ idx.price }}</span
              >
              <span
                class="text-xs font-semibold px-1.5 py-0.5 rounded"
                :class="
                  parseFloat(idx.change_percent) >= 0
                    ? 'text-red-600 bg-red-50'
                    : 'text-green-600 bg-green-50'
                "
              >
                {{ parseFloat(idx.change_percent) >= 0 ? "+" : ""
                }}{{ idx.change_percent }}%
              </span>
            </div>
          </div>
        </div>
        <!-- 涨跌统计卡片 -->
        <!-- <div class="bg-white rounded-xl p-3 shadow-sm border border-slate-100">
          <div class="text-xs text-slate-500 mb-2">涨跌统计</div>
          <div class="flex items-center justify-between">
            <div class="flex flex-col items-center">
              <span class="text-base font-bold text-red-500">{{ marketStats.rise_count || 0 }}</span>
              <span class="text-xs text-slate-400">上涨</span>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-base font-bold text-slate-500">{{ marketStats.flat_count || 0 }}</span>
              <span class="text-xs text-slate-400">平盘</span>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-base font-bold text-green-500">{{ marketStats.fall_count || 0 }}</span>
              <span class="text-xs text-slate-400">下跌</span>
            </div>
          </div>
          <div class="flex items-center justify-center gap-3 mt-2 pt-2 border-t border-slate-100">
            <span class="text-xs"><span class="inline-block w-2 h-2 bg-red-500 rounded-full mr-1"></span>涨停 {{ marketStats.limit_up || 0 }}</span>
            <span class="text-xs"><span class="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>跌停 {{ marketStats.limit_down || 0 }}</span>
          </div>
        </div> -->
      </div>

      <!-- 添加股票 -->
      <div class="flex gap-2 mb-4">
        <div class="relative flex-1">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </span>
          <input
            v-model="newStockCode"
            :placeholder="$t('dashboard.placeholder')"
            @keyup.enter="handleAddStock"
            :disabled="loading"
            class="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/70 transition-all duration-200 placeholder:text-slate-400"
          />
        </div>
        <button
          @click="handleAddStock"
          :disabled="loading"
          class="px-5 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm rounded-lg font-medium hover:from-blue-600 hover:to-blue-700 hover:shadow-md hover:shadow-blue-500/20 disabled:from-blue-300 disabled:to-blue-400 disabled:cursor-not-allowed transition-all duration-200 min-w-[72px] flex items-center justify-center gap-1.5"
        >
          <svg
            v-if="loading"
            class="animate-spin h-3.5 w-3.5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>{{
            loading ? $t("dashboard.adding") : $t("dashboard.add")
          }}</span>
        </button>
      </div>

      <!-- 错误提示 -->
      <div
        v-if="errorMsg"
        class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm"
      >
        {{ errorMsg }}
      </div>

      <!-- 预警通知 -->
      <div v-if="alertNotifications.length > 0" class="mb-4 space-y-2">
        <div
          v-for="(alert, idx) in alertNotifications"
          :key="idx"
          class="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm flex justify-between"
        >
          <div>
            <div class="font-medium">{{ alert.name }} ({{ alert.code }})</div>
            <div
              v-for="msg in alert.messages"
              :key="msg"
              class="text-amber-600"
            >
              {{ msg }}
            </div>
          </div>
          <button
            @click="dismissAlert(idx)"
            class="text-amber-400 hover:text-amber-600"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 分组和排序工具栏 -->
      <div class="flex items-center justify-between mb-3 px-1">
        <div class="flex items-center gap-2">
          <span class="text-sm text-slate-500 font-medium">分组:</span>
          <button
            @click="currentGroup = ''"
            :class="
              !currentGroup
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-sm shadow-blue-500/20'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 hover:border-slate-300'
            "
            class="px-3.5 py-1.5 text-xs rounded-lg transition-all duration-200 font-medium"
          >
            全部
          </button>
          <button
            v-for="g in groupList"
            :key="g"
            @click="currentGroup = g"
            @contextmenu="showGroupContextMenu($event, g)"
            :class="
              currentGroup === g
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-sm shadow-blue-500/20'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 hover:border-slate-300'
            "
            class="px-3.5 py-1.5 text-xs rounded-lg transition-all duration-200 font-medium"
          >
            {{ g }}
          </button>
          <button
            @click="showAddGroupModal = true"
            class="px-3 py-1.5 text-xs text-blue-500 bg-blue-50 border border-blue-100 rounded-lg hover:bg-blue-100 hover:border-blue-200 transition-all duration-200 font-medium"
          >
            + 新建
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-slate-500 font-medium">排序:</span>
          <select
            v-model="sortBy"
            class="text-xs bg-white border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-all duration-200 cursor-pointer"
          >
            <option value="">默认</option>
            <option value="change_desc">涨幅↓</option>
            <option value="change_asc">涨幅↑</option>
          </select>
        </div>
      </div>

      <!-- 股票列表 -->
      <div
        class="bg-white rounded-xl shadow-sm border border-slate-100"
      >
        <table class="w-full table-fixed">
          <thead>
            <tr
              class="bg-gradient-to-r from-slate-50 to-slate-100/50 border-b border-slate-100"
            >
              <th class="w-8 px-1 py-3.5"></th>
              <th
                class="w-24 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                代码
              </th>
              <th
                class="w-20 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                名称
              </th>
              <th
                class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                当前价
              </th>
              <th
                class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 cursor-pointer hover:text-blue-500 transition-colors uppercase tracking-wider"
                @click="toggleSort"
              >
                涨跌幅 {{ sortIcon }}
              </th>
              <th
                class="w-16 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                最高
              </th>
              <th
                class="w-16 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                最低
              </th>
              <th
                class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                成交额
              </th>
              <th
                class="w-16 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                分组
              </th>
              <th
                class="w-28 px-2 py-3.5 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr
              v-for="(stock, index) in filteredStocks"
              :key="stock.code"
              class="group hover:bg-gradient-to-r hover:from-slate-50 hover:to-transparent transition-all duration-200 cursor-pointer"
              draggable="true"
              @dragstart="handleDragStart(index, $event)"
              @dragover.prevent
              @drop="handleDrop(index)"
              @click="handleRowClick(stock.code, $event)"
              @contextmenu.prevent="showContextMenu($event, stock)"
            >
              <td class="px-1 py-3.5 cursor-move" @click.stop>
                <span
                  class="text-slate-300 group-hover:text-slate-500 text-sm font-bold transition-colors"
                  >⋮⋮</span
                >
              </td>
              <td class="px-2 py-3.5 text-xs font-mono text-slate-600">
                {{ stock.code }}
                <span
                  v-if="alerts[stock.code]?.enabled"
                  class="ml-0.5 text-amber-500"
                  >🔔</span
                >
              </td>
              <td
                class="px-2 py-3.5 text-sm font-medium text-slate-800 truncate"
              >
                {{ stock.name }}
              </td>
              <td
                class="px-2 py-3.5 text-sm text-right font-bold tabular-nums"
                :class="getPriceClass(stock.change_percent)"
              >
                {{ stock.price }}
              </td>
              <td class="px-2 py-3.5 text-right tabular-nums">
                <span
                  class="inline-flex items-center gap-0.5 text-sm font-semibold px-2 py-0.5 rounded-md"
                  :class="
                    parseFloat(stock.change_percent) > 0
                      ? 'text-red-600 bg-red-50'
                      : parseFloat(stock.change_percent) < 0
                      ? 'text-green-600 bg-green-50'
                      : 'text-slate-600 bg-slate-50'
                  "
                >
                  <span v-if="parseFloat(stock.change_percent) > 0">↑</span>
                  <span v-else-if="parseFloat(stock.change_percent) < 0"
                    >↓</span
                  >
                  {{ stock.change_percent }}%
                </span>
              </td>
              <td
                class="px-2 py-3.5 text-sm text-right text-slate-600 tabular-nums"
              >
                {{ stock.high }}
              </td>
              <td
                class="px-2 py-3.5 text-sm text-right text-slate-600 tabular-nums"
              >
                {{ stock.low }}
              </td>
              <td class="px-2 py-3.5 text-xs text-right text-slate-500">
                {{ formatAmount(stock.amount) }}
              </td>
              <td class="px-2 py-3.5 text-xs text-slate-500">
                <span
                  v-if="stockGroups[stock.code]"
                  class="px-2 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-600 rounded-md font-medium border border-blue-100"
                  >{{ stockGroups[stock.code] }}</span
                >
              </td>
              <td class="px-2 py-3.5 text-center" @click.stop>
                <div class="flex items-center justify-center gap-1.5">
                  <button
                    @click="handleSetFocus(stock.code)"
                    :class="
                      focusedStock === stock.code
                        ? 'bg-amber-100 text-amber-600 border-amber-300 shadow-sm'
                        : 'text-slate-400 border-slate-200 hover:bg-amber-50 hover:text-amber-500 hover:border-amber-200'
                    "
                    class="px-2 py-1 text-xs border rounded-lg transition-all duration-200"
                  >
                    ⭐
                  </button>
                  <button
                    @click="openAIModal(stock, 'fast')"
                    class="px-2 py-1 text-xs text-purple-500 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-all duration-200 font-medium"
                    title="快速AI分析"
                  >
                    AI
                  </button>
                  <button
                    @click="openAlertModal(stock)"
                    class="px-2 py-1 text-xs text-blue-500 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-all duration-200"
                  >
                    预警
                  </button>
                  <!-- 更多操作下拉菜单 -->
                  <div class="relative">
                    <button
                      @click.stop="toggleMoreMenu(stock.code)"
                      class="px-2 py-1 text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 hover:border-slate-300 transition-all duration-200"
                    >
                      ···
                    </button>
                    <div
                      v-if="moreMenuCode === stock.code"
                      class="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-xl border border-slate-200 py-1.5 z-30 min-w-[100px]"
                    >
                      <button
                        @click="openQuickTradeRecord(stock)"
                        class="w-full px-4 py-2 text-left text-xs text-slate-700 hover:bg-slate-50 transition-colors"
                      >
                        添加交易
                      </button>
                      <button
                        @click="handleRemoveStock(stock.code)"
                        class="w-full px-4 py-2 text-left text-xs text-red-500 hover:bg-red-50 transition-colors"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="filteredStocks.length === 0">
              <td
                colspan="10"
                class="px-4 py-12 text-center text-slate-400 text-sm"
              >
                {{ $t("dashboard.empty") }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 底部语录滚动 -->
      <div class="mt-4 h-6 overflow-hidden relative">
        <transition name="quote-fade" mode="out-in">
          <div
            :key="currentQuoteIndex"
            class="text-center text-xs text-slate-400 flex items-center justify-center gap-2"
          >
            <span class="text-slate-300">💡</span>
            <span>{{ stockQuotes[currentQuoteIndex] }}</span>
          </div>
        </transition>
      </div>
    </div>

    <!-- 分组右键菜单 -->
    <div
      v-if="groupContextMenu.show"
      class="fixed bg-white rounded-lg shadow-xl border border-slate-200 py-1 z-50 min-w-40"
      :style="{
        left: groupContextMenu.x + 'px',
        top: groupContextMenu.y + 'px',
      }"
      @click.stop
    >
      <div class="px-4 py-2 text-xs text-slate-400 border-b border-slate-100">
        {{ groupContextMenu.group }}
      </div>
      <button
        @click="handleDeleteGroup(false)"
        class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
      >
        🗑️ 删除分组
      </button>
      <button
        @click="handleDeleteGroup(true)"
        class="w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50"
      >
        ⚠️ 删除分组及股票
      </button>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.show"
      class="fixed bg-white rounded-lg shadow-xl border border-slate-200 py-1 z-50 min-w-32"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop
    >
      <button
        @click="handleContextAction('top')"
        class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
      >
        📌 置顶
      </button>
      <button
        @click="handleContextAction('bottom')"
        class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
      >
        📍 置底
      </button>
      <div class="border-t border-slate-100 my-1"></div>
      <div class="px-4 py-2 text-xs text-slate-400">移动到分组</div>
      <button
        @click="handleContextAction('group', '')"
        class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
      >
        无分组
      </button>
      <button
        v-for="g in groupList"
        :key="g"
        @click="handleContextAction('group', g)"
        class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
      >
        {{ g }}
        <span
          v-if="stockGroups[contextMenu.stock?.code] === g"
          class="text-blue-500"
          >✓</span
        >
      </button>
      <button
        @click="handleContextAction('newGroup')"
        class="w-full px-4 py-2 text-left text-sm text-blue-500 hover:bg-blue-50"
      >
        + 新建分组
      </button>
      <div class="border-t border-slate-100 my-1"></div>
      <button
        @click="handleContextAction('delete')"
        class="w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50"
      >
        🗑️ 删除
      </button>
    </div>

    <!-- 预警设置弹窗 -->
    <div
      v-if="showAlertModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeAlertModal"
    >
      <div class="bg-white rounded-xl shadow-xl w-96 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">
          预警设置 - {{ currentAlertStock?.name }}
        </h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1"
              >止盈价格</label
            >
            <input
              v-model="alertForm.take_profit"
              type="number"
              step="0.01"
              placeholder="价格达到时提醒"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1"
              >止损价格</label
            >
            <input
              v-model="alertForm.stop_loss"
              type="number"
              step="0.01"
              placeholder="价格跌至时提醒"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1"
              >涨跌幅预警 (%)</label
            >
            <input
              v-model="alertForm.change_alert"
              type="number"
              step="0.1"
              placeholder="涨跌幅达到时提醒"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div class="flex items-center gap-2">
            <input
              v-model="alertForm.enabled"
              type="checkbox"
              id="alert-enabled"
              class="w-4 h-4"
            />
            <label for="alert-enabled" class="text-sm text-slate-600"
              >启用预警</label
            >
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button
            @click="closeAlertModal"
            class="px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            取消
          </button>
          <button
            @click="saveAlert"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- 新建分组弹窗 -->
    <div
      v-if="showAddGroupModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closeAddGroupModal"
    >
      <div class="bg-white rounded-xl shadow-xl w-80 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">新建分组</h3>
        <p v-if="pendingGroupStock" class="text-xs text-slate-500 mb-2">
          创建后将把当前股票移动到此分组
        </p>
        <input
          v-model="newGroupName"
          placeholder="输入分组名称"
          @keyup.enter="addGroup"
          class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
        />
        <div class="flex justify-end gap-3">
          <button
            @click="closeAddGroupModal"
            class="px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            取消
          </button>
          <button
            @click="addGroup"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            确定
          </button>
        </div>
      </div>
    </div>

    <!-- AI 分析弹窗 -->
    <AIAnalysisModal
      v-model:visible="showAiModal"
      :stock-code="aiStockCode"
      :type="aiType"
    />

    <!-- 更新日志弹窗 -->
    <ChangelogModal v-model:visible="showChangelog" />

    <!-- 使用手册弹窗 -->
    <UserGuideModal v-model:visible="showUserGuide" />

    <!-- 大盘详情弹窗 -->
    <IndexDetailModal
      v-model:visible="showIndexDetail"
      :index-code="currentIndexCode"
    />

    <!-- 快速添加交易记录弹窗 -->
    <TradeRecordModal
      v-model:visible="showQuickTradeModal"
      :stock-code="quickTradeStockCode"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import {
  getStocks,
  addStock,
  removeStock,
  getSettings,
  reorderStocks,
  setAlert,
  getTriggeredAlerts,
  setFocusedStock,
  setStockGroup,
  addGroupApi,
  deleteGroupApi,
  getMarketStats,
} from "../api";
import AIAnalysisModal from "./AIAnalysisModal.vue";
import ChangelogModal from "./ChangelogModal.vue";
import UserGuideModal from "./UserGuideModal.vue";
import TradeRecordModal from "./TradeRecordModal.vue";
import IndexDetailModal from "./IndexDetailModal.vue";

const { locale } = useI18n();
const emit = defineEmits(["openSettings", "openDetail", "openJournal"]);

// 市场涨跌统计
const marketStats = ref<any>({});

// 响应式状态
const newStockCode = ref("");
const stockData = ref<any[]>([]);
const stockOrder = ref<string[]>([]); // 保存原始顺序
const alerts = ref<Record<string, any>>({});
const stockGroups = ref<Record<string, string>>({});
const indexData = ref<Record<string, any>>({});
const loading = ref(false);
const errorMsg = ref("");
const refreshInterval = ref(5);
const alertNotifications = ref<any[]>([]);
const focusedStock = ref<string | null>(null);

// 分组和排序
const currentGroup = ref("");
const sortBy = ref("");
const groupList = ref<string[]>([]);
const newGroupName = ref("");
const showAddGroupModal = ref(false);
const pendingGroupStock = ref<string | null>(null); // 待分组的股票代码（右键菜单新建分组时使用）

// 拖拽状态
const dragIndex = ref<number | null>(null);

// 右键菜单
const contextMenu = ref({ show: false, x: 0, y: 0, stock: null as any });

// 分组右键菜单
const groupContextMenu = ref({ show: false, x: 0, y: 0, group: "" });

// 预警弹窗
const showAlertModal = ref(false);
const currentAlertStock = ref<any>(null);
const alertForm = ref({
  take_profit: "",
  stop_loss: "",
  change_alert: "",
  enabled: true,
});

// AI 分析
const showAiModal = ref(false);
const aiStockCode = ref("");
const aiType = ref<"fast" | "precise">("fast");

// 更新日志和使用手册
const showChangelog = ref(false);
const showUserGuide = ref(false);

// 底部语录
const stockQuotes = [
  // 财报与规则认知
  "一季报披露：4月1日-4月30日",
  "中报披露：7月1日-8月31日",
  "三季报披露：10月1日-10月31日",
  "年报披露：次年1月1日-4月30日",
  "投资有风险，入市需谨慎",

  // 趋势与节奏
  "补强不补弱，顺势而为",
  "不要和趋势作对，趋势是你最好的朋友",
  "牛市不言顶，熊市不言底",
  "在高潮时警惕，在退潮时理智",
  "高位横盘不突破，久盘必跌",
  "宁可错过，不可做错",

  // 量价与技术信号
  "量在价先，成交量是股价的先行指标",
  "底部放量要注意，顶部放量要警惕",

  // 纪律 / 风控 / 心态
  "截断亏损，让利润奔跑",
  "空仓也是一种操作",
  "卖飞光荣，套牢可耻",
  "会买的是徒弟，会卖的是师傅",
  "不要把所有鸡蛋放在一个篮子里",
  "知行合一，严格执行交易纪律",
  "市场永远是对的，错的只是自己",
];

const currentQuoteIndex = ref(0);
let quoteIntervalId: ReturnType<typeof setInterval> | null = null;

// 大盘详情弹窗
const showIndexDetail = ref(false);
const currentIndexCode = ref("");

// 更多操作菜单
const moreMenuCode = ref<string | null>(null);

// 快速添加交易记录
const showQuickTradeModal = ref(false);
const quickTradeStockCode = ref("");

const toggleMoreMenu = (code: string) => {
  moreMenuCode.value = moreMenuCode.value === code ? null : code;
};

const openQuickTradeRecord = (stock: any) => {
  moreMenuCode.value = null;
  quickTradeStockCode.value = stock.code;
  showQuickTradeModal.value = true;
};

// 点击外部关闭更多菜单
const handleClickOutsideMoreMenu = (e: MouseEvent) => {
  if (moreMenuCode.value) {
    moreMenuCode.value = null;
  }
};

const openAIModal = (stock: any, type: "fast" | "precise") => {
  aiStockCode.value = stock.code;
  aiType.value = type;
  showAiModal.value = true;
};

// 打开大盘详情
const openIndexDetail = (code: string) => {
  currentIndexCode.value = code;
  showIndexDetail.value = true;
};

let intervalId: ReturnType<typeof setInterval> | null = null;
let alertCheckId: ReturnType<typeof setInterval> | null = null;

// 大盘指数列表
const indexList = computed(() => {
  const codes = ["sh000001", "sz399001", "sz399006", "sh000300"];
  return codes.map((c) => indexData.value[c]).filter(Boolean);
});

// 排序图标
const sortIcon = computed(() => {
  if (sortBy.value === "change_desc") return "↓";
  if (sortBy.value === "change_asc") return "↑";
  return "";
});

// 过滤和排序后的股票列表
const filteredStocks = computed(() => {
  let list = [...stockData.value];

  // 按分组过滤
  if (currentGroup.value) {
    list = list.filter((s) => stockGroups.value[s.code] === currentGroup.value);
  }

  // 排序
  if (sortBy.value === "change_desc") {
    list.sort(
      (a, b) => parseFloat(b.change_percent) - parseFloat(a.change_percent)
    );
  } else if (sortBy.value === "change_asc") {
    list.sort(
      (a, b) => parseFloat(a.change_percent) - parseFloat(b.change_percent)
    );
  }

  return list;
});

const toggleLanguage = () => {
  locale.value = locale.value === "en" ? "zh" : "en";
};

const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent);
  if (value > 0) return "text-red-500";
  if (value < 0) return "text-green-500";
  return "text-slate-600";
};

const getIndexClass = (changePercent: string) => {
  const value = parseFloat(changePercent || "0");
  if (value > 0) return "text-red-500";
  if (value < 0) return "text-green-500";
  return "text-slate-800";
};

const formatAmount = (amount: string) => {
  const val = parseFloat(amount || "0");
  if (val >= 100000000) return (val / 100000000).toFixed(2) + "亿";
  if (val >= 10000) return (val / 10000).toFixed(0) + "万";
  return val.toFixed(0);
};

const toggleSort = () => {
  if (sortBy.value === "") sortBy.value = "change_desc";
  else if (sortBy.value === "change_desc") sortBy.value = "change_asc";
  else sortBy.value = "";
};

// 拖拽排序 - 修复：保存到后端后不立即刷新
const handleDragStart = (index: number, e: DragEvent) => {
  dragIndex.value = index;
  if (e.dataTransfer) e.dataTransfer.effectAllowed = "move";
};

const handleDrop = async (targetIndex: number) => {
  if (dragIndex.value === null || dragIndex.value === targetIndex) {
    dragIndex.value = null;
    return;
  }

  // 在当前过滤列表中操作
  const list = filteredStocks.value;
  const draggedStock = list[dragIndex.value];

  // 更新原始顺序
  const newOrder = [...stockOrder.value];
  const fromIdx = newOrder.indexOf(draggedStock.code);
  const targetStock = list[targetIndex];
  const toIdx = newOrder.indexOf(targetStock.code);

  if (fromIdx !== -1 && toIdx !== -1) {
    newOrder.splice(fromIdx, 1);
    newOrder.splice(toIdx, 0, draggedStock.code);
    stockOrder.value = newOrder;

    // 重新排列 stockData
    const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
    stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);

    // 保存到后端
    await reorderStocks(newOrder);
  }

  dragIndex.value = null;
};

// 右键菜单
const showContextMenu = (e: MouseEvent, stock: any) => {
  contextMenu.value = { show: true, x: e.clientX, y: e.clientY, stock };
};

const hideContextMenu = () => {
  contextMenu.value.show = false;
  groupContextMenu.value.show = false;
};

// 分组右键菜单
const showGroupContextMenu = (e: MouseEvent, group: string) => {
  e.preventDefault();
  groupContextMenu.value = { show: true, x: e.clientX, y: e.clientY, group };
};

const handleDeleteGroup = async (deleteStocks: boolean) => {
  const group = groupContextMenu.value.group;
  if (!group) return;

  const res = await deleteGroupApi(group, deleteStocks);
  if (res.status === "success") {
    // 从本地分组列表移除
    groupList.value = groupList.value.filter((g) => g !== group);

    if (deleteStocks && res.deleted_stocks?.length > 0) {
      // 如果删除了股票，更新本地数据
      stockOrder.value = stockOrder.value.filter(
        (c) => !res.deleted_stocks.includes(c)
      );
      stockData.value = stockData.value.filter(
        (s) => !res.deleted_stocks.includes(s.code)
      );
      for (const code of res.deleted_stocks) {
        delete stockGroups.value[code];
      }
    } else {
      // 仅删除分组，清除股票的分组标记
      for (const code in stockGroups.value) {
        if (stockGroups.value[code] === group) {
          delete stockGroups.value[code];
        }
      }
    }

    // 如果当前选中的是被删除的分组，切换到全部
    if (currentGroup.value === group) {
      currentGroup.value = "";
    }
  }

  hideContextMenu();
};

const handleContextAction = async (action: string, param?: string) => {
  const stock = contextMenu.value.stock;
  if (!stock) return;

  if (action === "top") {
    const newOrder = [
      stock.code,
      ...stockOrder.value.filter((c) => c !== stock.code),
    ];
    stockOrder.value = newOrder;
    const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
    stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);
    await reorderStocks(newOrder);
  } else if (action === "bottom") {
    const newOrder = [
      ...stockOrder.value.filter((c) => c !== stock.code),
      stock.code,
    ];
    stockOrder.value = newOrder;
    const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]));
    stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean);
    await reorderStocks(newOrder);
  } else if (action === "group") {
    await setStockGroup(stock.code, param || "");
    if (param) {
      stockGroups.value[stock.code] = param;
      if (!groupList.value.includes(param)) groupList.value.push(param);
    } else {
      delete stockGroups.value[stock.code];
    }
  } else if (action === "newGroup") {
    // 记住当前股票，打开新建分组弹窗
    pendingGroupStock.value = stock.code;
    showAddGroupModal.value = true;
  } else if (action === "delete") {
    await handleRemoveStock(stock.code);
  }

  hideContextMenu();
};

// 关闭新建分组弹窗
const closeAddGroupModal = () => {
  showAddGroupModal.value = false;
  newGroupName.value = "";
  pendingGroupStock.value = null;
};

// 新建分组
const addGroup = async () => {
  if (!newGroupName.value) return;

  const groupName = newGroupName.value.trim();
  if (!groupName) return;

  // 调用后端 API 持久化分组
  await addGroupApi(groupName);

  // 更新本地分组列表
  if (!groupList.value.includes(groupName)) {
    groupList.value.push(groupName);
  }

  // 如果是从右键菜单新建分组，将当前股票移动到新分组
  if (pendingGroupStock.value) {
    await setStockGroup(pendingGroupStock.value, groupName);
    stockGroups.value[pendingGroupStock.value] = groupName;
  }

  closeAddGroupModal();
};

// 预警弹窗
const openAlertModal = (stock: any) => {
  currentAlertStock.value = stock;
  const existing = alerts.value[stock.code];
  alertForm.value = {
    take_profit: existing?.take_profit || "",
    stop_loss: existing?.stop_loss || "",
    change_alert: existing?.change_alert || "",
    enabled: existing?.enabled ?? true,
  };
  showAlertModal.value = true;
};

const closeAlertModal = () => {
  showAlertModal.value = false;
  currentAlertStock.value = null;
};

const saveAlert = async () => {
  if (!currentAlertStock.value) return;
  await setAlert(currentAlertStock.value.code, alertForm.value);
  alerts.value[currentAlertStock.value.code] = { ...alertForm.value };
  closeAlertModal();
};

const dismissAlert = (index: number) => {
  alertNotifications.value.splice(index, 1);
};

// 更新托盘
const updateTray = () => {
  if (stockData.value.length > 0) {
    const summary = stockData.value
      .slice(0, 3)
      .map((s) => `${s.name}: ${s.price} (${s.change_percent}%)`)
      .join("\n");
    (window as any).ipcRenderer?.send("update-tray", summary);
  }
};

const updateTrayIcon = (focusedData: any) => {
  if (focusedData) {
    (window as any).ipcRenderer?.send("update-tray-icon", {
      change: focusedData.change_percent,
      price: focusedData.price,
      name: focusedData.name,
    });
  }
};

const handleSetFocus = async (code: string) => {
  await setFocusedStock(code);
  focusedStock.value = code;
  const stock = stockData.value.find((s) => s.code === code);
  if (stock) updateTrayIcon(stock);
};

const handleRowClick = (code: string, event: MouseEvent) => {
  if ((event.target as HTMLElement).closest("button")) return;
  emit("openDetail", code);
};

// 获取数据 - 修复：不覆盖用户的排序
const fetchData = async () => {
  try {
    const res = await getStocks();

    // 首次加载时保存原始顺序
    if (stockOrder.value.length === 0) {
      stockOrder.value = res.stocks;
    }

    // 按照本地保存的顺序排列数据
    const dataMap = res.data;
    stockData.value = stockOrder.value
      .map((code: string) => dataMap[code])
      .filter(Boolean);

    alerts.value = res.alerts || {};
    stockGroups.value = res.groups || {};
    indexData.value = res.index_data || {};
    focusedStock.value =
      res.focused_stock || (res.stocks.length > 0 ? res.stocks[0] : null);

    // 更新分组列表（从后端获取的 group_list 优先，再合并已使用的分组）
    const usedGroups = new Set(Object.values(stockGroups.value));
    const backendGroups = res.group_list || [];
    const allGroups = new Set([...backendGroups, ...usedGroups]);
    groupList.value = Array.from(allGroups) as string[];

    updateTray();
    if (res.focused_data) updateTrayIcon(res.focused_data);

    // 获取市场涨跌统计
    // fetchMarketStats();
  } catch (error) {
    console.error("获取数据失败:", error);
  }
};

// 获取市场涨跌统计
// const fetchMarketStats = async () => {
//   try {
//     const res = await getMarketStats();
//     if (res.status === "success") {
//       marketStats.value = res.stats || {};
//     }
//   } catch (e) {
//     console.error("获取涨跌统计失败:", e);
//   }
// };

const checkAlerts = async () => {
  try {
    const res = await getTriggeredAlerts();
    if (res.alerts?.length > 0) {
      alertNotifications.value.push(...res.alerts);
      for (const alert of res.alerts) {
        const title = `📈 ${alert.name} 预警触发`;
        const body = alert.messages.join("\n") + `\n当前价: ${alert.price}`;
        (window as any).ipcRenderer?.showNotification(title, body);
      }
    }
  } catch (e) {
    console.error("检查预警失败:", e);
  }
};

const handleAddStock = async () => {
  if (!newStockCode.value) return;
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await addStock(newStockCode.value);
    if (res.status === "error") {
      errorMsg.value = res.message;
    } else {
      // 添加到本地顺序
      const normalizedCode =
        newStockCode.value.startsWith("sh") ||
        newStockCode.value.startsWith("sz")
          ? newStockCode.value
          : newStockCode.value.startsWith("6")
          ? `sh${newStockCode.value}`
          : `sz${newStockCode.value}`;
      if (
        !stockOrder.value.includes(normalizedCode) &&
        !stockOrder.value.includes(newStockCode.value)
      ) {
        stockOrder.value.push(normalizedCode);
      }
      newStockCode.value = "";
      await fetchData();
    }
  } catch (e) {
    errorMsg.value = "添加失败，请检查后端连接";
  } finally {
    loading.value = false;
  }
};

const handleRemoveStock = async (code: string) => {
  await removeStock(code);
  stockOrder.value = stockOrder.value.filter((c) => c !== code);
  stockData.value = stockData.value.filter((s) => s.code !== code);
};

const loadSettingsAndStart = async () => {
  try {
    const res = await getSettings();
    if (res.status === "success" && res.settings?.refresh_interval) {
      refreshInterval.value = res.settings.refresh_interval;
    }
  } catch (e) {
    console.error("加载设置失败:", e);
  }

  await fetchData();
  intervalId = setInterval(fetchData, refreshInterval.value * 1000);
  alertCheckId = setInterval(checkAlerts, 3000);
};

// 点击其他地方关闭右键菜单和更多操作菜单
const handleGlobalClick = () => {
  hideContextMenu();
  moreMenuCode.value = null;
};

onMounted(() => {
  loadSettingsAndStart();
  document.addEventListener("click", handleGlobalClick);
  // 启动语录轮播
  quoteIntervalId = setInterval(() => {
    currentQuoteIndex.value =
      (currentQuoteIndex.value + 1) % stockQuotes.length;
  }, 5000);
});

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
  if (alertCheckId) clearInterval(alertCheckId);
  if (quoteIntervalId) clearInterval(quoteIntervalId);
  document.removeEventListener("click", handleGlobalClick);
});
</script>

<style scoped>
/* 语录渐隐过渡动画 */
.quote-fade-enter-active,
.quote-fade-leave-active {
  transition: all 0.5s ease;
}
.quote-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.quote-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
