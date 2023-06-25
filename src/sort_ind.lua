local read, write
do
  local _obj_0 = io
  read, write = _obj_0.read, _obj_0.write
end
local byte, char
do
  local _obj_0 = string
  byte, char = _obj_0.byte, _obj_0.char
end
local concat, insert, sort
do
  local _obj_0 = table
  concat, insert, sort = _obj_0.concat, _obj_0.insert, _obj_0.sort
end
local normalizeLatin
normalizeLatin = function(str, ind)
  local unimask = "[%z\1-\127\194-\244][\128-\191]*"
  if not str then
    return ""
  end
  return str:gsub(unimask, (function(unichar)
    local charmap = "AÀÁÂÃÄÅĀĂĄǍǞǠǺȀȂȦȺ" .. "AEÆǢǼ" .. "BßƁƂƄɃ" .. "CÇĆĈĊČƆƇȻ" .. "DÐĎĐƉƊ" .. "DZƻǄǱ" .. "Dzǅǲ" .. "EÈÉÊËĒĔĖĘĚƎƏƐȄȆȨɆ" .. "FƑ" .. "GĜĞĠĢƓǤǦǴ" .. "HĤĦȞ" .. "HuǶ" .. "IÌÍÎÏĨĪĬĮİƖƗǏȈȊ" .. "IJĲ" .. "JĴɈ" .. "KĶƘǨ" .. "LĹĻĽĿŁȽ" .. "LJǇ" .. "Ljǈ" .. "NÑŃŅŇŊƝǸȠ" .. "NJǊ" .. "Njǋ" .. "OÒÓÔÕÖØŌŎŐƟƠǑǪǬǾȌȎȪȬȮȰ" .. "OEŒ" .. "OIƢ" .. "OUȢ" .. "PÞƤǷ" .. "QɊ" .. "RŔŖŘȐȒɌ" .. "SŚŜŞŠƧƩƪƼȘ" .. "TŢŤŦƬƮȚȾ" .. "UÙÚÛÜŨŪŬŮŰŲƯƱƲȔȖɄǓǕǗǙǛ" .. "VɅ" .. "WŴƜ" .. "YÝŶŸƳȜȲɎ" .. "ZŹŻŽƵƷƸǮȤ" .. "aàáâãäåāăąǎǟǡǻȁȃȧ" .. "aeæǣǽ" .. "bƀƃƅ" .. "cçćĉċčƈȼ" .. "dðƌƋƍȡďđ" .. "dbȸ" .. "dzǆǳ" .. "eèéêëēĕėęěǝȅȇȩɇ" .. "fƒ" .. "gĝğġģƔǥǧǵ" .. "hĥħȟ" .. "hvƕ" .. "iìíîïĩīĭįıǐȉȋ" .. "ijĳ" .. "jĵǰȷɉ" .. "kķĸƙǩ" .. "lĺļľŀłƚƛȴ" .. "ljǉ" .. "nñńņňŉŋƞǹȵ" .. "njǌ" .. "oòóôõöøōŏőơǒǫǭǿȍȏȫȭȯȱ" .. "oeœ" .. "oiƣ" .. "ouȣ" .. "pþƥƿ" .. "qɋ" .. "qpȹ" .. "rŕŗřƦȑȓɍ" .. "sśŝşšſƨƽșȿ" .. "tţťŧƫƭțȶ" .. "tsƾ" .. "uùúûüũūŭůűųưǔǖǘǚǜȕȗ" .. "wŵ" .. "yýÿŷƴȝȳɏ" .. "zźżžƶƹƺǯȥɀ" .. ""
    unichar = unichar:gsub('[%(%)%.%%%+%-%*%?%[%^%$]', '%%%0')
    return unichar:match("%a") or charmap:match("(%a+)[^%a]-" .. unichar)
  end), ind)
end
local tri
tri = function(a, b)
  return normalizeLatin(b[3]:match("[^,]*")):lower() > normalizeLatin(a[3]:match("[^,]*")):lower()
end
local _mt = {
  __tostring = function(self)
    return concat((function()
      local _accum_0 = { }
      local _len_0 = 1
      for _index_0 = 1, #self do
        local e = self[_index_0]
        _accum_0[_len_0] = tostring(e)
        _len_0 = _len_0 + 1
      end
      return _accum_0
    end)())
  end
}
local _lettre = "a"
local traiter
traiter = function(lignes, idx, idt)
  local t = setmetatable({ }, _mt)
  while lignes[idx] and #lignes[idx][1] >= idt do
    if #lignes[idx][1] == idt then
      if lignes[idx][2] ~= "\\indexspace" then
        t[#t + 1] = setmetatable(lignes[idx], _mt)
      end
      idx = idx + 1
    elseif #lignes[idx][1] > idt then
      local _t = t[#t]
      local res
      res, idx = traiter(lignes, idx, #lignes[idx][1])
      for _index_0 = 1, #res do
        local l = res[_index_0]
        _t[#_t + 1] = l
      end
    end
  end
  sort(t, tri)
  local i = 1
  while i <= #t do
    local l = t[i]
    if l[2] == "\\item" and normalizeLatin(l[3]:sub(2, 2)):lower() >= _lettre then
      insert(t, i, "\n  \\indexspace\n\n" .. tostring(l))
      _lettre = char(byte(normalizeLatin(l[3]:sub(2, 2)):lower()) + 1)
    end
    i = i + 1
  end
  return t, idx
end
local lignes
do
  local _accum_0 = { }
  local _len_0 = 1
  for l in read("*a"):gsub("\n%s*\\hyperpage", " \\hyperpage"):gmatch("([^\n]+\n?)") do
    _accum_0[_len_0] = {
      l:match("(%s*)(\\?%S*)([^,]*)(,?.*)")
    }
    _len_0 = _len_0 + 1
  end
  lignes = _accum_0
end
local idx = 1
while idx < #lignes do
  local output
  output, idx = traiter(lignes, idx, 0)
  write(tostring(output) .. "\n")
end
