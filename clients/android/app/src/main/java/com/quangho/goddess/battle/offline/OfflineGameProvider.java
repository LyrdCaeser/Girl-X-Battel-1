package com.quangho.goddess.battle.offline;

import android.content.Context;

import com.quangho.goddess.battle.BattleRuntimeBridge;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Small, deterministic offline gameplay provider. The JSON file is the authoritative
 * local save; every mutation is written through a temporary file and renamed atomically.
 */
public final class OfflineGameProvider {
    private static final int SAVE_VERSION = 3;
    private final Context context;
    private final File saveFile;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private JSONObject save;

    public OfflineGameProvider(Context context) throws IOException {
        this.context = context.getApplicationContext();
        this.saveFile = new File(this.context.getFilesDir(), "offline/profile.json");
        load();
    }

    /** File-backed constructor for JVM contract tests; production uses the Context constructor. */
    OfflineGameProvider(File filesDirectory) throws IOException {
        this.context = null;
        this.saveFile = new File(filesDirectory, "offline/profile.json");
        load();
    }

    public OfflineLocalApi.Response state() {
        lock.readLock().lock();
        try { return ok(copy(save)); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response partners() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("partners", save.optJSONArray("roster"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response formation() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("partners", save.optJSONArray("formation"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response inventory() {
        lock.readLock().lock();
        try { return ok(new JSONObject().put("items", save.optJSONObject("items"))); }
        catch (JSONException error) { return error(500, "offline_state_invalid"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response graduatePreview(String body) {
        lock.readLock().lock();
        try {
            JSONObject request = object(body);
            JSONObject h = hero(request.optInt("partner_id", 0));
            if (h == null) return error(404, "partner_not_found");
            int stars = h.optInt("stars", 5);
            JSONObject before = new JSONObject().put("hp", h.optInt("hp", 0)).put("atk", h.optInt("atk", 0)).put("arm", h.optInt("arm", 0)).put("power", h.optInt("power", 0));
            JSONObject after = new JSONObject().put("hp", h.optInt("hp", 0) + 100).put("atk", h.optInt("atk", 0) + 20).put("arm", h.optInt("arm", 0) + 12).put("power", h.optInt("power", 0) + 48);
            return ok(new JSONObject().put("from_star", stars).put("to_star", Math.min(10, stars + 1)).put("level", h.optInt("lv", 1)).put("level_cap_before", levelCap(h)).put("level_cap_after", levelCap(h) + 20).put("before", before).put("after", after).put("local", true));
        } catch (JSONException error) { return error(400, "invalid_star_recipe"); }
        finally { lock.readLock().unlock(); }
    }

    public OfflineLocalApi.Response profile(String body) {
        lock.writeLock().lock();
        try {
            JSONObject request = object(body);
            JSONObject profile = save.optJSONObject("profile");
            if (profile == null) { profile = new JSONObject(); put(save, "profile", profile); }
            for (String key : new String[] {"name", "avatar", "signature"}) {
                if (request.has(key)) put(profile, key, request.optString(key, ""));
            }
            persist();
            return ok(new JSONObject().put("state", copy(save)));
        } catch (IOException | JSONException error) {
            return error(500, "offline_save_failed");
        } finally { lock.writeLock().unlock(); }
    }

    public OfflineLocalApi.Response action(String body) {
        lock.writeLock().lock();
        try {
            JSONObject request = object(body);
            String message = request.optString("message", "");
            JSONObject data = request.optJSONObject("data");
            if ("SET_HANG_TEAM".equals(message)) {
                if (data == null || !data.has("partners")) return error(400, "invalid_team");
                JSONArray formation = normalizeFormation(data.optJSONArray("partners"));
                if (formation.length() == 0) return error(400, "empty_team");
                put(save, "formation", formation);
                persist();
                return ok(new JSONObject().put("state", copy(save)));
            }
            if ("SUMMON".equals(message)) return summon(data);
            if ("SHOP_BUY".equals(message)) return shopBuy(data);
            if ("HOME_ACTION".equals(message)) return homeAction(data);
            if ("EVENT_ACTION".equals(message)) return eventAction(data);
            if ("STORY_ACTION".equals(message)) return storyAction(data);
            if ("EQUIPMENT_ACTION".equals(message)) return equipmentAction(data);
            if ("PARTNER_LEVUP".equals(message)) return levelUp(data);
            if ("PARTNER_GRADEUP".equals(message)) return gradeUp(data);
            if ("AWAKE_PARTNER".equals(message)) return awake(data);
            if ("COMPOSE_PARTNER".equals(message)) return compose(data);
            if ("MAP_FIGHT".equals(message)) return fight(data);
            return error(501, "offline_action_not_implemented");
        } catch (IOException | JSONException error) {
            return error(500, "offline_save_failed");
        } finally { lock.writeLock().unlock(); }
    }

    public OfflineLocalApi.Response battle(long id) {
        lock.readLock().lock();
        try {
            JSONObject reports = save.optJSONObject("battle_reports");
            JSONObject report = reports == null ? null : reports.optJSONObject(Long.toString(id));
            return report == null ? error(404, "battle_not_found") : ok(report);
        } finally { lock.readLock().unlock(); }
    }

    private OfflineLocalApi.Response summon(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_summon_request");
        int id = data.optInt("summon_id", 0), times = data.optInt("times", 1);
        if (times != 1 && times != 10) return error(400, "invalid_summon_times");
        int item, amount, freeSeconds = 0, bonusItem = 0, bonus = 0;
        switch (id) {
            case 1: item = 33; amount = times; break;
            case 2: item = 33; amount = 10; times = 10; break;
            case 3: item = 0; amount = 0; freeSeconds = 8 * 60 * 60; break;
            case 4: item = 2; amount = times == 10 ? 2200 : 250; bonusItem = 12; bonus = times == 10 ? 100 : 10; break;
            case 5: item = 2; amount = 2200; times = 10; bonusItem = 12; bonus = 100; break;
            case 6: item = 36; amount = times; break;
            case 7: item = 36; amount = 10; times = 10; break;
            case 8: item = 0; amount = 0; freeSeconds = 48 * 60 * 60; bonusItem = 12; bonus = 10; break;
            case 9: item = 12; amount = 1000; break;
            case 15: item = 11; amount = 10; break;
            case 16: item = 11; amount = 100; times = 10; break;
            case 22: item = 2; amount = 250; bonusItem = 12; bonus = 10; break;
            case 23: item = 2; amount = 2200; times = 10; bonusItem = 12; bonus = 100; break;
            case 24: item = 36; amount = 1; bonusItem = 12; bonus = 10; break;
            case 25: item = 36; amount = 10; times = 10; bonusItem = 12; bonus = 100; break;
            case 26: item = 0; amount = 0; freeSeconds = 24 * 60 * 60; bonusItem = 12; bonus = 10; break;
            default: return error(400, "summon_not_available_offline");
        }
        JSONObject items = save.optJSONObject("items");
        if (amount > 0 && (items == null || items.optInt(Integer.toString(item), 0) < amount)) return error(409, "insufficient_resources");
        JSONObject summon = save.optJSONObject("summon");
        if (summon == null) { summon = new JSONObject(); put(save, "summon", summon); }
        long now = System.currentTimeMillis() / 1000L; String freeKey = "free_at_" + id;
        if (freeSeconds > 0 && times != 1) return error(400, "free_summon_single_only");
        if (freeSeconds > 0 && now < summon.optLong(freeKey, 0L)) return error(409, "summon_free_cooldown");
        if (amount > 0) put(items, Integer.toString(item), items.optInt(Integer.toString(item), 0) - amount);
        if (freeSeconds > 0) put(summon, freeKey, now + freeSeconds);
        JSONArray results = new JSONArray(); JSONArray roster = save.optJSONArray("roster");
        for (int n = 0; n < times; n++) {
            int partnerId = save.optInt("next_partner_id", 2); put(save, "next_partner_id", partnerId + 1);
            JSONObject partner = new JSONObject().put("partner_id", partnerId).put("table_id", 41001 + (partnerId % 5))
                    .put("name", "Offline Summon #" + partnerId).put("lv", 1).put("stars", 5).put("grade", 0)
                    .put("max_grade", 5).put("level_cap", 20).put("atk", 100).put("arm", 80).put("hp", 1000).put("power", 347);
            roster.put(partner); results.put(partner);
        }
        if (bonus > 0) put(items, Integer.toString(bonusItem), items.optInt(Integer.toString(bonusItem), 0) + bonus);
        put(summon, "last_summon_id", id); put(summon, "last_summon_at", now);
        JSONArray history = summon.optJSONArray("history"); if (history == null) { history = new JSONArray(); put(summon, "history", history); }
        history.put(new JSONObject().put("summon_id", id).put("times", times).put("at", now).put("results", results));
        while (history.length() > 50) history.remove(0);
        persist(); return ok(new JSONObject().put("summon_res", results).put("state", copy(save)));
    }

    private OfflineLocalApi.Response shopBuy(JSONObject data) throws JSONException, IOException {
        if (data == null || data.optInt("shop", 0) != 7 || data.optInt("index", 0) != 1) return error(400, "shop_not_available_offline");
        int num = data.optInt("num", 1); if (num < 1 || num > 10) return error(400, "invalid_shop_item");
        JSONObject items = save.optJSONObject("items"); int cost = 100 * num;
        if (items == null || items.optInt("1", 0) < cost) return error(409, "insufficient_resources");
        put(items, "1", items.optInt("1", 0) - cost); put(items, "3", items.optInt("3", 0) + 10 * num);
        JSONObject boards = save.optJSONObject("shop_boards"); if (boards == null) { boards = new JSONObject(); put(save, "shop_boards", boards); }
        JSONObject board = boards.optJSONObject("7"); if (board == null) { board = new JSONObject(); put(boards, "7", board); }
        put(board, "bought_1", board.optInt("bought_1", 0) + num); persist();
        return ok(new JSONObject().put("got", new JSONObject().put("3", 10 * num)).put("state", copy(save)));
    }

    private OfflineLocalApi.Response homeAction(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_home_action");
        JSONObject home = save.optJSONObject("home_systems"); if (home == null) { home = new JSONObject(); put(save, "home_systems", home); }
        String action = data.optString("action", "");
        if ("pet_select".equals(action)) put(home, "selected_pet", data.optInt("id", 0));
        else if ("travel_start".equals(action)) { put(home, "started_travel", true); put(home, "travel_started_at", System.currentTimeMillis() / 1000L); }
        else if ("travel_collect".equals(action)) {
            if (!home.optBoolean("started_travel", false)) return error(409, "production_not_started");
            put(save.optJSONObject("items"), "3", save.optJSONObject("items").optInt("3", 0) + 10);
            put(home, "travel_started_at", System.currentTimeMillis() / 1000L);
        } else return error(501, "home_action_not_implemented_offline");
        persist(); return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response eventAction(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_event_action");
        JSONObject events = save.optJSONObject("events"); if (events == null) { events = new JSONObject(); put(save, "events", events); }
        String action = data.optString("action", ""); JSONObject items = save.optJSONObject("items"); JSONObject awards = new JSONObject();
        long today = System.currentTimeMillis() / 86400000L;
        if (events.optLong("checkin_day", -1L) != today) { put(events, "checkin_day", today); put(events, "checkin_claimed_today", false); }
        if ("visit".equals(action)) put(events, "online_days", Math.max(1, events.optInt("online_days", 0)));
        else if ("checkin".equals(action)) {
            if (events.optBoolean("checkin_claimed_today", false)) return error(409, "event_already_claimed");
            put(events, "checkin_claimed_today", true); put(awards, "3", 50);
        } else if ("sevenday".equals(action)) {
            int claimed = events.optInt("sevenday_claimed", 0); if (claimed >= 7) return error(409, "event_complete");
            put(events, "sevenday_claimed", claimed + 1); put(awards, "9", 100);
        } else return error(501, "event_action_not_implemented_offline");
        java.util.Iterator<String> keys = awards.keys(); while (keys.hasNext()) { String key = keys.next(); put(items, key, items.optInt(key, 0) + awards.optInt(key, 0)); }
        persist(); return ok(new JSONObject().put("awards", awards).put("state", copy(save)));
    }

    private OfflineLocalApi.Response storyAction(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_story_action");
        JSONObject story = save.optJSONObject("story"); if (story == null) { story = new JSONObject(); put(save, "story", story); }
        JSONArray seen = story.optJSONArray("seen"); if (seen == null) { seen = new JSONArray(); put(story, "seen", seen); }
        String action = data.optString("action", "");
        if ("seen".equals(action)) { int plot = data.optInt("plot", 0); if (plot > 0 && !contains(seen, plot)) seen.put(plot); }
        else if ("unlock".equals(action)) {
            JSONObject items = save.optJSONObject("items"); int key = 208, cost = 2;
            if (items.optInt(Integer.toString(key), 0) < cost) return error(409, "insufficient_story_keys");
            int id = data.optInt("id", 0); if (id <= 0) return error(400, "invalid_story_section");
            put(items, Integer.toString(key), items.optInt(Integer.toString(key), 0) - cost);
            JSONArray unlocked = story.optJSONArray("unlocked"); if (unlocked == null) { unlocked = new JSONArray(); put(story, "unlocked", unlocked); }
            if (!contains(unlocked, id)) unlocked.put(id);
        } else return error(501, "story_action_not_implemented_offline");
        persist(); return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response equipmentAction(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_equipment_action");
        JSONObject hero = hero(data.optInt("partner_id", 0)); if (hero == null) return error(404, "partner_not_found");
        JSONArray equipment = hero.optJSONArray("equipment"); if (equipment == null) { equipment = new JSONArray(); put(hero, "equipment", equipment); }
        while (equipment.length() < 6) equipment.put(0);
        int slot = data.optInt("slot", 0); if (slot < 1 || slot > 6) return error(400, "invalid_equipment_slot");
        String action = data.optString("action", ""); JSONObject items = save.optJSONObject("items");
        if ("unequip".equals(action)) put(equipment, slot - 1, 0);
        else if ("equip".equals(action)) {
            int item = data.optInt("item_id", 0); if (item <= 0 || items.optInt(Integer.toString(item), 0) < 1) return error(409, "equipment_not_owned");
            int old = equipment.optInt(slot - 1, 0); put(items, Integer.toString(item), items.optInt(Integer.toString(item), 0) - 1);
            if (old > 0) put(items, Integer.toString(old), items.optInt(Integer.toString(old), 0) + 1); put(equipment, slot - 1, item);
        } else return error(501, "equipment_action_not_implemented_offline");
        persist(); return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response fight(JSONObject data) throws JSONException, IOException {
        if (data == null) return error(400, "invalid_battle_request");
        int stage = data.optInt("stage_id", 1);
        if (stage < 1 || stage > 30) return error(400, "invalid_stage");
        if (stage > save.optInt("next_stage", 1)) return error(409, "stage_locked");
        JSONArray team = data.optJSONArray("partners");
        if (team == null) team = save.optJSONArray("formation");
        team = normalizeFormation(team);
        if (team == null || team.length() == 0) return error(400, "empty_team");
        String input = battleInput(team, stage);
        JSONObject report;
        try {
            report = new JSONObject(BattleRuntimeBridge.runBattle(context, "battle", input));
        } catch (RuntimeException error) {
            return error(503, "offline_battle_engine_unavailable");
        }
        long id = save.optLong("next_battle_id", 1L);
        put(save, "next_battle_id", id + 1L);
        JSONObject summary = new JSONObject();
        put(summary, "id", id); put(summary, "stage", stage);
        boolean win = report.optBoolean("isWin", false);
        put(summary, "win", win);
        boolean firstClear = win && !contains(clearedArray(), stage);
        JSONObject awarded = firstClear ? rewards(stage) : new JSONObject();
        put(summary, "rewards", awarded);
        if (firstClear) addItems(awarded);
        JSONObject reports = save.optJSONObject("battle_reports");
        if (reports == null) { reports = new JSONObject(); put(save, "battle_reports", reports); }
        put(reports, Long.toString(id), report);
        put(save, "last_battle", summary);
        JSONArray cleared = save.optJSONArray("cleared");
        if (cleared == null) { cleared = new JSONArray(); put(save, "cleared", cleared); }
        if (firstClear) cleared.put(stage);
        put(save, "max_stage", Math.max(save.optInt("max_stage", 0), firstClear ? stage : 0));
        put(save, "next_stage", Math.min(30, Math.max(save.optInt("next_stage", 1), firstClear ? stage + 1 : save.optInt("next_stage", 1))));
        if (win) {
            JSONArray stages = save.optJSONArray("stages");
            if (stages != null) {
                for (int i = 0; i < stages.length(); i++) {
                    JSONObject current = stages.optJSONObject(i);
                    if (current != null && current.optInt("id", -1) <= stage + 1) put(current, "unlocked", true);
                    if (current != null && current.optInt("id", -1) == stage) put(current, "cleared", true);
                }
            }
        }
        put(save, "formation", team);
        put(report, "display_units", displayUnits(team, stage));
        put(report, "map_asset", "battle_map_26_1");
        persist();
        return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response levelUp(JSONObject data) throws JSONException, IOException {
        JSONObject hero = hero(data == null ? 0 : data.optInt("partner_id", 0));
        if (hero == null) return error(404, "partner_not_found");
        int increment = data.optInt("incr_lv", 1);
        if (increment < 1 || increment > 10) return error(400, "invalid_level_increment");
        int level = hero.optInt("lv", 1), cap = levelCap(hero);
        if (level + increment > cap) return error(409, "level_cap_reached");
        JSONObject cost = new JSONObject();
        for (int next = level + 1; next <= level + increment; next++) {
            addCost(cost, "1", 100 * next);
            addCost(cost, "9", 10 * next);
        }
        if (!canAfford(cost)) return error(409, "insufficient_resources");
        spend(cost); put(hero, "lv", level + increment); refreshStats(hero); persist();
        return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response gradeUp(JSONObject data) throws JSONException, IOException {
        JSONObject hero = hero(data == null ? 0 : data.optInt("partner_id", 0));
        if (hero == null) return error(404, "partner_not_found");
        int grade = hero.optInt("grade", 0), max = hero.optInt("max_grade", 5);
        if (grade >= max) return error(409, "grade_max_reached");
        if (hero.optInt("lv", 1) < levelCap(hero)) return error(409, "level_cap_required");
        JSONObject cost = hero.optJSONObject("grade_cost");
        if (cost == null) cost = new JSONObject().put("1", 500 * (grade + 1));
        if (!canAfford(cost)) return error(409, "insufficient_resources");
        spend(cost); put(hero, "grade", grade + 1); refreshStats(hero); persist();
        return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response awake(JSONObject data) throws JSONException, IOException {
        int baseId = data == null ? 0 : data.optInt("partner_id", 0);
        JSONObject base = hero(baseId); JSONArray materialIds = data == null ? null : data.optJSONArray("material_ids");
        if (base == null || materialIds == null || materialIds.length() == 0) return error(400, "invalid_star_recipe");
        int stars = base.optInt("stars", 5);
        if (stars >= 10) return error(409, "star_max_reached");
        JSONArray consumed = validateMaterials(materialIds, baseId);
        for (int i = 0; i < consumed.length(); i++) removeHero(consumed.getInt(i));
        put(base, "stars", stars + 1); put(base, "level_cap", 20 + (stars) * 20); refreshStats(base);
        persist(); return ok(new JSONObject().put("state", copy(save)));
    }

    private OfflineLocalApi.Response compose(JSONObject data) throws JSONException, IOException {
        if (data == null || !data.has("table_id")) return error(400, "invalid_star_recipe");
        JSONArray ids = data.optJSONArray("material_ids");
        if (ids == null || ids.length() < 2) return error(400, "invalid_star_recipe");
        int baseId = ids.optInt(0, 0); JSONObject base = hero(baseId);
        if (base == null) return error(404, "partner_not_found");
        JSONArray materialOnly = new JSONArray();
        for (int i = 1; i < ids.length(); i++) materialOnly.put(ids.optInt(i, 0));
        JSONArray consumed = validateMaterials(materialOnly, baseId);
        for (int i = 0; i < consumed.length(); i++) removeHero(consumed.getInt(i));
        put(base, "table_id", data.optInt("table_id"));
        put(base, "stars", Math.min(10, Math.max(6, base.optInt("stars", 5) + 1))); refreshStats(base);
        persist(); return ok(new JSONObject().put("state", copy(save)));
    }

    private JSONArray validateMaterials(JSONArray ids, int baseId) throws JSONException {
        JSONArray consumed = new JSONArray();
        java.util.HashSet<Integer> seen = new java.util.HashSet<>();
        for (int i = 0; i < ids.length(); i++) {
            int id = ids.optInt(i, 0); if (id == 0 || id == baseId || !seen.add(id) || hero(id) == null) throw new JSONException("invalid_materials");
            consumed.put(id);
        }
        return consumed;
    }

    private JSONObject hero(int id) { JSONArray roster = save.optJSONArray("roster"); if (roster == null) return null; for (int i=0;i<roster.length();i++) { JSONObject h=roster.optJSONObject(i); if (h!=null && h.optInt("partner_id",-1)==id) return h; } return null; }
    private int levelCap(JSONObject h) { return h.optInt("level_cap", 20 + h.optInt("grade",0) * 20); }
    private void refreshStats(JSONObject h) throws JSONException { int lv=h.optInt("lv",1), stars=h.optInt("stars",5), grade=h.optInt("grade",0); put(h,"atk",100+lv*20+stars*15+grade*30); put(h,"arm",80+lv*12+stars*10+grade*20); put(h,"hp",1000+lv*100+stars*80+grade*200); put(h,"power",h.optInt("atk",0)+h.optInt("arm",0)+h.optInt("hp",0)/6); JSONObject next=new JSONObject(); put(next,"1",100*(lv+1)); put(next,"9",10*(lv+1)); put(h,"next_cost",next); }
    private void addCost(JSONObject c,String id,int n) { put(c,id,c.optInt(id,0)+n); }
    private boolean canAfford(JSONObject c) { JSONObject items=save.optJSONObject("items"); java.util.Iterator<String> it=c.keys(); while(it.hasNext()){String k=it.next(); if(items==null || items.optInt(k,0)<c.optInt(k,0)) return false;} return true; }
    private void spend(JSONObject c) { JSONObject items=save.optJSONObject("items"); java.util.Iterator<String> it=c.keys(); while(it.hasNext()){String k=it.next(); put(items,k,items.optInt(k,0)-c.optInt(k,0));} }
    private void addItems(JSONObject c) { JSONObject items=save.optJSONObject("items"); java.util.Iterator<String> it=c.keys(); while(it.hasNext()){String k=it.next(); put(items,k,items.optInt(k,0)+c.optInt(k,0));} }
    private JSONArray clearedArray() { JSONArray a=save.optJSONArray("cleared"); if(a==null){a=new JSONArray();put(save,"cleared",a);} return a; }
    private void removeHero(int id) { JSONArray roster=save.optJSONArray("roster"); if(roster==null)return; for(int i=roster.length()-1;i>=0;i--) if(roster.optJSONObject(i)!=null&&roster.optJSONObject(i).optInt("partner_id",-1)==id) roster.remove(i); JSONArray formation=save.optJSONArray("formation"); if(formation!=null) for(int i=formation.length()-1;i>=0;i--) if(formation.optJSONObject(i)!=null&&formation.optJSONObject(i).optInt("partner_id",-1)==id) formation.remove(i); }
    private JSONArray normalizeFormation(JSONArray input) { JSONArray out=new JSONArray(); if(input==null)return out; java.util.HashSet<Integer> slots=new java.util.HashSet<>(); for(int i=0;i<input.length()&&out.length()<6;i++){JSONObject requested=input.optJSONObject(i);if(requested==null)continue;JSONObject owned=hero(requested.optInt("partner_id",0));if(owned==null)continue;int pos=requested.optInt("pos",out.length()+1);if(pos<1||pos>6||!slots.add(pos))continue;JSONObject canonical=copy(owned);put(canonical,"pos",pos);out.put(canonical);} return out; }
    private JSONArray displayUnits(JSONArray team,int stage) throws JSONException { JSONArray out=new JSONArray(); for(int i=0;i<team.length()&&i<6;i++){JSONObject p=team.optJSONObject(i);if(p==null)continue;JSONObject u=new JSONObject(p.toString());put(u,"pos",p.optInt("pos",i+1));put(u,"level",p.optInt("lv",1));put(u,"name",p.optString("name","Ally "+p.optInt("partner_id",i+1)));out.put(u);} JSONObject enemy=new JSONObject().put("pos",7).put("table_id",1).put("level",1).put("name","Enemy").put("boss",false);out.put(enemy);return out; }

    private static JSONObject rewards(int stage) throws JSONException {
        return new JSONObject().put("1", 1000 + stage * 100).put("3", 50 + stage * 5).put("9", 100 + stage * 10);
    }

    private static String battleInput(JSONArray team, int stage) throws JSONException {
        StringBuilder out = new StringBuilder("{teamA=");
        out.append("{");
        int count = Math.min(6, team.length());
        for (int i = 0; i < count; i++) {
            if (i > 0) out.append(",");
            JSONObject p = team.optJSONObject(i);
            if (p == null) p = new JSONObject();
            out.append("{table_id=").append(Math.max(1, p.optInt("table_id", 41001)))
                    .append(",partner_id=").append(Math.max(1, p.optInt("partner_id", i + 1)))
                    .append(",lv=").append(Math.max(1, p.optInt("lv", 1)))
                    .append(",pos=").append(Math.max(1, Math.min(6, p.optInt("pos", i + 1)))).append("}");
        }
        // Runtime positions are local to each side; team B is exposed as 7..12 in the report.
        out.append("},teamB={{table_id=1,isMonster=true,pos=1}},battle_id=").append(100000 + stage)
                .append(",random_seed=").append(1000 + stage).append("}");
        return out.toString();
    }

    private void load() throws IOException {
        lock.writeLock().lock();
        try {
            if (!saveFile.isFile()) { save = initial(); persist(); return; }
            byte[] bytes;
            try (FileInputStream in = new FileInputStream(saveFile)) { bytes = readAll(in); }
            save = migrate(new JSONObject(new String(bytes, StandardCharsets.UTF_8)));
            persist();
        } catch (JSONException error) { throw new IOException("Corrupt offline save", error); }
        finally { lock.writeLock().unlock(); }
    }

    private static JSONObject initial() throws JSONException {
        JSONObject s = new JSONObject();
        put(s, "save_version", SAVE_VERSION); put(s, "revision", 0L); put(s, "level", 1); put(s, "max_stage", 0);
        put(s, "next_stage", 1); put(s, "cleared", new JSONArray());
        put(s, "items", new JSONObject().put("1", 10000).put("2", 3000).put("3", 1000)
                .put("9", 1000).put("11", 100).put("12", 1000).put("33", 20).put("36", 20));
        put(s, "profile", new JSONObject().put("name", "Offline Player").put("avatar", "41001"));
        put(s, "formation", new JSONArray().put(new JSONObject().put("table_id", 41001).put("partner_id", 1).put("lv", 1).put("pos", 1)));
        put(s, "roster", new JSONArray().put(new JSONObject()
                .put("partner_id", 1).put("table_id", 41001).put("name", "Gwen")
                .put("lv", 1).put("stars", 5).put("grade", 0).put("max_grade", 5).put("level_cap", 20)
                .put("next_cost", new JSONObject().put("1", 100).put("9", 10))
                .put("atk", 100).put("arm", 80).put("hp", 1000).put("power", 347)));
        JSONArray stages = new JSONArray();
        for (int i = 1; i <= 30; i++) stages.put(new JSONObject().put("id", i).put("chapter", 1).put("level_required", 1).put("unlocked", i == 1));
        put(s, "stages", stages); put(s, "battle_reports", new JSONObject()); put(s, "next_battle_id", 1L);
        put(s, "next_partner_id", 2); put(s, "summon", new JSONObject().put("history", new JSONArray()));
        put(s, "shop_boards", new JSONObject()); put(s, "home_systems", new JSONObject().put("selected_pet", 0).put("started_travel", false));
        return s;
    }

    /**
     * Upgrades the pre-MVP save shape without discarding campaign progress. Version zero
     * files were written before the durable save contract was pinned and may only contain
     * profile/formation/cleared fields. Missing MVP fields receive the same deterministic
     * defaults as a new guest profile.
     */
    static JSONObject migrate(JSONObject legacy) throws JSONException, IOException {
        int version = legacy.optInt("save_version", 0);
        if (version > SAVE_VERSION) throw new IOException("Unsupported offline save version");
        if (version == SAVE_VERSION) return legacy;
        JSONObject defaults = initial();
        copyIfMissing(legacy, defaults, "revision");
        copyIfMissing(legacy, defaults, "level");
        copyIfMissing(legacy, defaults, "next_stage");
        copyIfMissing(legacy, defaults, "cleared");
        copyIfMissing(legacy, defaults, "items");
        copyIfMissing(legacy, defaults, "profile");
        copyIfMissing(legacy, defaults, "formation");
        copyIfMissing(legacy, defaults, "roster");
        copyIfMissing(legacy, defaults, "stages");
        copyIfMissing(legacy, defaults, "battle_reports");
        copyIfMissing(legacy, defaults, "next_battle_id");
        copyIfMissing(legacy, defaults, "max_stage");
        copyIfMissing(legacy, defaults, "next_partner_id");
        copyIfMissing(legacy, defaults, "summon");
        copyIfMissing(legacy, defaults, "shop_boards");
        copyIfMissing(legacy, defaults, "home_systems");
        JSONObject items = legacy.optJSONObject("items");
        JSONObject defaultItems = defaults.optJSONObject("items");
        if (items == null) { items = new JSONObject(); legacy.put("items", items); }
        for (String key : new String[] {"2", "3", "9", "11", "12", "33", "36"})
            if (!items.has(key)) items.put(key, defaultItems.optInt(key, 0));
        JSONArray roster=legacy.optJSONArray("roster"); if(roster!=null) for(int i=0;i<roster.length();i++){JSONObject h=roster.optJSONObject(i);if(h!=null){if(!h.has("grade"))put(h,"grade",0);if(!h.has("max_grade"))put(h,"max_grade",5);if(!h.has("level_cap"))put(h,"level_cap",20);}}
        legacy.put("save_version", SAVE_VERSION);
        return legacy;
    }

    private static void copyIfMissing(JSONObject target, JSONObject defaults, String key) throws JSONException {
        if (!target.has(key)) target.put(key, defaults.get(key));
    }

    private void persist() throws IOException {
        put(save, "revision", save.optLong("revision", 0L) + 1L);
        File parent = saveFile.getParentFile(); if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("Cannot create save directory");
        File tmp = new File(saveFile.getPath() + ".tmp");
        try (FileOutputStream out = new FileOutputStream(tmp)) { out.write(save.toString().getBytes(StandardCharsets.UTF_8)); out.getFD().sync(); }
        if (!tmp.renameTo(saveFile)) {
            try { java.nio.file.Files.move(tmp.toPath(), saveFile.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING); }
            catch (java.io.IOException error) { if (!tmp.delete()) { /* best effort cleanup */ } throw new IOException("Cannot atomically replace offline save", error); }
        }
    }

    private static byte[] readAll(FileInputStream in) throws IOException { byte[] b = new byte[8192]; java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream(); int n; while ((n = in.read(b)) >= 0) out.write(b, 0, n); return out.toByteArray(); }
    private static JSONObject copy(JSONObject source) { try { return new JSONObject(source.toString()); } catch (JSONException e) { throw new IllegalStateException(e); } }
    private static JSONObject object(String raw) throws JSONException { return raw == null ? new JSONObject() : new JSONObject(raw); }
    private static boolean contains(JSONArray a, int value) { for (int i = 0; i < a.length(); i++) if (a.optInt(i, -1) == value) return true; return false; }
    private static OfflineLocalApi.Response ok(JSONObject body) { return new OfflineLocalApi.Response(200, body); }
    private static OfflineLocalApi.Response error(int status, String code) {
        JSONObject body = new JSONObject();
        put(body, "error", code); put(body, "offline", true);
        return new OfflineLocalApi.Response(status, body);
    }
    private static void put(JSONObject o, String k, Object v) { try { o.put(k, v); } catch (JSONException e) { throw new IllegalStateException(e); } }
}
