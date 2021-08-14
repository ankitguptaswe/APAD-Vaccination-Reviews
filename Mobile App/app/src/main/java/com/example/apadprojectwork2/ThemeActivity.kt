package com.example.apadprojectwork2

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.ActionBar
import androidx.recyclerview.widget.LinearLayoutManager
import com.android.volley.Response
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import kotlinx.android.synthetic.main.activity_theme.*
import kotlinx.android.synthetic.main.theme_row.*
import kotlinx.android.synthetic.main.theme_row.view.*

class ThemeActivity() : AppCompatActivity() {
    private  lateinit var actionBar: ActionBar

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_theme)
        recyclerView_main.layoutManager = LinearLayoutManager(this)
        actionBar = supportActionBar!!
        actionBar.title = "Themes"
        fetchThemes()
    }

    fun onSeeReviewClick(view: View) {
        val intent = Intent(this@ThemeActivity, ReviewActivity::class.java)
        intent.putExtra("Theme", textView_review_title.text)
        startActivity(intent)
    }

    fun fetchThemes() {
        val queue = Volley.newRequestQueue(this)
        val url = "https://apad-vaccine-reviews.uc.r.appspot.com/themes/all"
        val stringRequest = object: StringRequest(
            Method.GET, url,
            Response.Listener { response ->
                val strResp = response.toString()
                var result: List<String> = strResp.split("]").map { it.trim() }
                var themes: List<String> = result[0].drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                var descriptions: List<String> = result[1].drop(1).drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                var pictures: List<String> = result[2].drop(1).drop(1).drop(1).dropLast(1).replace("\"", "").split(",").map { it.trim() }
                val themeFeed = Themes(themes, descriptions, pictures)
                runOnUiThread {
                    recyclerView_main.adapter = ThemeAdapter(themeFeed)
                }
            },
            Response.ErrorListener {  })
        {
            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["source"] = "android"
                return headers
            }
        }
        queue.add(stringRequest)
    }
}