import json
import random
import collections
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from readmdict import MDX
from taggit.models import Tag

from .forms import *
from .models import *
from .web_query import find_synonym


class CardListView(ListView):
    model = Card
    template_name = 'flashcards/list.html'


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card
    template_name = 'flashcards/back3.html'


# card_detail函数版
def card_detailview(request, card_id):
    # 获取card实例
    card = get_object_or_404(Card, id=card_id)
    return render(request,
                  'flashcards/back3.html',
                  {'object': card,
                   'tags': card.tags.all()})


# 背诵
@login_required
def cardreciteview(request, card_id, rank):
    # 获取card实例
    card = get_object_or_404(Card, id=card_id)

    # 创建并保存
    recitedata = Recitedata(rank=rank, card=card)
    recitedata.save()
    # 生成随机数并跳转至下一卡片
    card = Card.objects.filter(id=str(random.randrange(1, 7000, 1)))[0]
    return redirect(card.get_absolute_url())


# 下一张卡片
@login_required
def nextcardview(request):
    card = Card.objects.filter(id=str(random.randrange(1, 7000, 1)))[0]
    return redirect(card.get_absolute_url())


# 展示数据
@login_required
def recitedatadisplay(request):
    # 按rank排序，后续改进
    recitedata = Recitedata.objects.order_by("rank")
    # 使用set以防止card重复
    cards = set([data.card for data in recitedata])
    datas = [{'card': card, 'recitedata': card.recitedata.all()} for card in cards]
    return render(request,
                  'flashcards/recitedata.html',
                  {'datas': datas})


@login_required
def search(request):
    cards = []
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        cards = Card.objects.filter(
            Q(question__icontains=cd['query']) | Q(example__icontains=cd['query']))
    if cd['query'] == '':
        form = SearchForm()
    # 将搜索字段替换为红色
    for card in cards:
        card.question = card.question.replace(cd['query'], "<span id='red'><b>" + cd['query'] + "</b></span>")
        card.example = card.example.replace(cd['query'], "<span id='red'><b>" + cd['query'] + "</b></span>")
    return render(request, 'flashcards/search.html', {'cards': cards, 'searchvalue': cd['query'], 'form': form})


# 首页
@login_required
def index(request):
    cards = Card.objects.all()
    form = SearchForm()
    type_proportion = {
        'cihui': len(Card.objects.filter(group__startswith='词汇')),
        'duanyu': len(Card.objects.filter(group__startswith='短语')),
        'bianxi': len(Card.objects.filter(group__startswith='辨析'))
    }
    # 获取当前用户的单词列表
    wordlists = request.user.owner.all()
    # 获取过去七天的背诵数据
    now = timezone.now()
    start = now - timedelta(days=7, hours=now.hour, minutes=now.minute, seconds=now.second)
    recitedata = Recitedata.objects.filter(date__gt=start)
    rank_count_by_day = []
    for i in range(1, 8):
        all_data = recitedata.filter(date__gt=start + timedelta(days=i), date__lt=start + timedelta(days=i + 1))
        counter = collections.Counter([data.rank for data in all_data])
        rank_count_by_day.append([counter[1], counter[2], counter[3], counter[4]])
    rank_count_by_rank = []
    for i in range(0, 4):
        rank_count_by_rank.append([rank_day[i] for rank_day in rank_count_by_day])

    return render(request, 'flashcards/anki.html',
                  {'len': len(cards),
                   'type_proportion': type_proportion,
                   'lenlist': len(WordList.objects.all()),
                   'form': form,
                   'wordlists': wordlists,
                   'tags': Tag.objects.all(),
                   'recitedata': rank_count_by_rank, },

                  )


# 删除背诵记录
@login_required
def undo(request, card_id):
    # 需要撤回的卡片和需要删除背诵记录的卡是一张卡
    card = Card.objects.filter(id=card_id)
    card[0].recitedata.latest('date').delete()

    return redirect(card[0].get_absolute_url())


# 删除背诵记录
@login_required
def undo_list(request, card_id, list_id, progress):
    # 需要撤回的卡片和需要删除背诵记录的卡是一张卡
    card = Card.objects.filter(id=card_id)
    card[0].recitedata.latest('date').delete()
    # 修改进度
    return redirect('flashcards:recite_wordlist', list_id, progress, 0)


# 网络搜索
@login_required
def websearch(request):
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        words = find_synonym(cd['query'])
    else:
        form = SearchForm()
        words = []
    return render(request, 'flashcards/webquery.html',
                  {"words": words, 'searchvalue': cd['query'], 'form': form}, )


@login_required
def dict_search(request):
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        # 加载mdx文件
        filename = "flashcards/static/dict/剑桥高阶.mdx"
        headwords = [*MDX(filename)]  # 单词名列表
        items = [*MDX(filename).items()]  # 释义html源码列表
        # if len(headwords) == len(items):
        #     print(f'加载成功：共{len(headwords)}条')
        # else:
        #     print(f'【ERROR】加载失败{len(headwords)}，{len(items)}')

        # 查词，返回单词和html文件

        queryWord = cd['query']

        # print(headwords[120:123])
        html_result = ''
        try:
            wordIndex = headwords.index(queryWord.encode())
            word, html = items[wordIndex]
            word, html_result = word.decode(), html.decode()
        except ValueError:
            html_result = 'No Results!'
    else:
        form = SearchForm()
        html_result = ''

    return render(request, 'flashcards/dict.html',
                  {'html_result': html_result, 'form': form, 'searchvalue': cd['query']})


@login_required
def create_wordlist_by_diff(request):
    cd = {"query": 'list'}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
    # 找到最近的三个复习data并累计，生成一个字典
    rank_sum_dict = map(lambda card: {'id': card.id, 'rank_sum': sum(
        sorted([Recitedata.rank for Recitedata in card.recitedata.order_by('-date')], reverse=True)[0:3])
    if len(card.recitedata.all()) > 2
    else sum([Recitedata.rank for Recitedata in card.recitedata.order_by('-date')])}
                        , Card.objects.all())
    # 按rank排序，取前五十个值
    # 不知道为什么id列表总为空
    # id_list = [dic['id'] for dic in sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]]
    # id_list = list(
    #     map(lambda dic: dic['id'], sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]))
    # print(id_list)
    sort_list = sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]
    wordlist = WordList(owner=request.user, name=cd['query'], wordlist=json.dumps(sort_list)
                        , len_list=len(sort_list))
    wordlist.save()
    messages.success(request, '单词列表创建成功')
    return redirect('flashcards:dashboard')


@login_required
def create_wordlist_by_tag(request):
    cd = {"query": 'list', "tag": 'marked'}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
    tag = get_object_or_404(Tag, slug=request.GET['tag'])
    cards = Card.objects.filter(tags__in=[tag])
    id_list = [{'id': card.id} for card in cards]
    wordlist = WordList(owner=request.user, name=cd['query'], wordlist=json.dumps(id_list)
                        , len_list=len(id_list))
    wordlist.save()
    messages.success(request, '单词列表创建成功')
    return redirect('flashcards:dashboard')


@login_required
def recite_wordlist(request, wordlist_id, progress, rank):
    wordlist = WordList.objects.filter(id=wordlist_id)[0]
    # 判断请求progress和数据库progress是否相等，若不同，则将后者覆盖（在重新复习的时候可能出现的问题）
    if progress == 0 and wordlist.progress != 0:
        wordlist.progress = progress

    # json解析单词列表id
    id_list = list(map(lambda dic: dic['id'], json.loads(wordlist.wordlist)))
    # 判断是刚进入还是进入后第一次提交卡片
    # 若提交，则更新进度
    # 若刚进入，则不更新进度

    if rank > 0:
        # 获取当前card实例
        current_card = get_object_or_404(Card, id=id_list[progress])
        # 创建并保存记忆数据
        recitedata = Recitedata(rank=rank, card=current_card)
        recitedata.save()

        # 计算完成度
        wordlist.progress = progress + 1
        percentage = int((wordlist.progress / wordlist.len_list) * 100)
        # 更新进度
        wordlist.save()
    else:
        percentage = int((wordlist.progress / wordlist.len_list) * 100)

    # 进度更新后判断是否完成单词列表，若完成，则返回主页
    if wordlist.progress == wordlist.len_list:
        messages.success(request, '您已背完该单词列表！')
        return redirect('flashcards:dashboard')
    # 获取下一个单词
    # 必须使用数据库中的wordlist.progress，否则使用progress会导致第一个不更新
    next_word = get_object_or_404(Card, id=id_list[wordlist.progress])

    return render(request, 'flashcards/recite_wordlist.html',
                  {
                      "percentage": percentage,
                      'object': next_word,
                      'progress': wordlist.progress,
                      'wordlist_id': wordlist_id,
                      'tags': next_word.tags.all(),
                      'section': 'list',
                  })


@login_required
def delete_wordlist(request, wordlist_id):
    get_object_or_404(WordList, id=wordlist_id).delete()
    messages.success(request, '单词列表删除成功')
    return redirect('flashcards:dashboard')


@login_required
def word_add_tags(request, word_id, tag, section):
    word = get_object_or_404(Card, id=word_id)
    word.tags.add(tag)
    messages.success(request, '标签添加成功')
    if section == 0:
        return redirect('flashcards:card_detail', card_id=word_id)
    else:
        return redirect('flashcards:recite_wordlist', wordlist_id=section,
                        progress=get_object_or_404(WordList, id=section).progress, rank=0)


@login_required
def word_delete_tags(request, word_id, tag, section):
    word = get_object_or_404(Card, id=word_id)
    word.tags.remove(tag)
    messages.success(request, '标签删除成功')
    if section == 0:
        return redirect('flashcards:card_detail', card_id=word_id)
    else:
        return redirect('flashcards:recite_wordlist', wordlist_id=section,
                        progress=get_object_or_404(WordList, id=section).progress, rank=0)
